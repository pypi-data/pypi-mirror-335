import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import traceback
import os

from mcpx_py import Chat, mcp_run, openai_compatible_model
import pystache

from .models import ScoreModel, Score, Results, Test, Model
from .database import Database
from .constants import SYSTEM_PROMPT, TEST_PROMPT

logger = logging.getLogger(__name__)


class ModelApiConfig:
    """Helper class to manage model API configurations."""

    @staticmethod
    def get_host_url(model_name: str, provider: str) -> str:
        """Get the appropriate API host URL for a given model and provider."""
        if provider in ["ollama", "llama"]:
            host = os.environ.get(
                f"{model_name.upper()}_HOST",
                os.environ.get(
                    "LLAMA_HOST",
                    os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434"),
                ),
            )
            return f"{host}/v1" if not host.endswith("/v1") else host
        elif provider == "openai":
            host = os.environ.get(
                f"{model_name.upper()}_HOST",
                os.environ.get("OPENAI_HOST", "https://api.openai.com"),
            )
            return f"{host}/v1" if not host.endswith("/v1") else host
        return ""

    @staticmethod
    def get_model_config(model: Model) -> str:
        """Get the appropriate model configuration for API calls."""
        if model.provider in ["ollama", "llama", "openai"]:
            host = ModelApiConfig.get_host_url(model.name, model.provider)
            return openai_compatible_model(host, model.name)
        return model.name


class ToolAnalysis:
    """Helper class to analyze tool usage patterns."""

    def __init__(self):
        self.tool_analysis: Dict[str, Any] = {}
        self.redundant_tool_calls = 0
        self.seen_tool_patterns = set()
        self.total_tool_calls = 0

    def analyze_message(self, msg: Dict[str, Any], index: int) -> None:
        """Analyze a single message for tool usage patterns."""
        if not msg.get("tool"):
            return

        tool_name = msg["tool"]["name"]
        tool_input = msg["tool"]["input"]
        self.total_tool_calls += 1

        # Create pattern string for redundancy detection
        tool_pattern = f"{tool_name}:{str(tool_input)}"

        # Check for redundancy
        redundancy_status = (
            "redundant" if tool_pattern in self.seen_tool_patterns else "unique"
        )
        if redundancy_status == "redundant":
            self.redundant_tool_calls += 1
        else:
            self.seen_tool_patterns.add(tool_pattern)

        # Store tool analysis
        self.tool_analysis[f"tool_{index}"] = {
            "name": tool_name,
            "input": tool_input,
            "redundancy": redundancy_status,
        }


class Judge:
    """Evaluates model performance on given tests."""

    model: str
    models: List[Model]
    ignore_tools: List[str]
    db: Database
    profile: Optional[str]

    def __init__(
        self,
        models: Optional[List[Model | str]] = None,
        db: Optional[Database] = None,
        profile: Optional[str] = None,
        judge_model: str = "claude-3-5-sonnet-latest",
        ignore_tools: Optional[List[str]] = None,
    ):
        self.profile = profile or mcp_run.ProfileSlug("~", "default")
        self.ignore_tools = ignore_tools or []
        self.db = db or Database()
        self.models = []
        if models is not None:
            for model in models:
                self.add_model(model)

    def add_model(
        self,
        model: Model | str,
        profile: Optional[str] = None,
    ) -> None:
        """Add a model to the evaluation list."""
        if isinstance(model, str):
            model = Model(name=model)
        if profile is not None:
            model.profile = profile
        self.models.append(model)

    async def run_test(self, test: Test, save: bool = True) -> Results:
        """Run a specific test configuration."""
        profile = test.profile
        if profile is None:
            profile = self.profile or mcp_run.ProfileSlug("~", "default")
        else:
            profile = mcp_run.ProfileSlug.parse(profile)

        if test.task is not None:
            client = mcp_run.Client(config=mcp_run.ClientConfig(profile=profile))
            tasks = client.tasks
            if test.task not in tasks:
                raise Exception(f"Invalid task, {test.task} not found in {profile}")
            test.prompt = tasks[test.task].prompt

        results = await self.run(
            pystache.render(test.prompt, test.vars),
            test.check,
            test.expected_tools,
        )

        if save:
            self.db.save_results(test.name, results)
        return results

    async def evaluate_model(
        self,
        model: Model,
        prompt: str,
        tool_analysis: ToolAnalysis,
    ) -> Dict[str, Any]:
        """Evaluate a single model's performance."""
        result = {"messages": [], "tools-available": []}

        try:
            model_config = ModelApiConfig.get_model_config(model)
            chat = Chat(
                client=mcp_run.Client(
                    config=mcp_run.ClientConfig(profile=model.profile)
                ),
                model=model_config,
                ignore_tools=self.ignore_tools,
                system_prompt=TEST_PROMPT,
                retries=5,
            )
            # Get available tools, handling both real and mock objects
            try:
                result["tools-available"] = list(chat.client.tools.keys())
            except (TypeError, AttributeError):
                # If tools is a mock object, get the return value directly
                result["tools-available"] = chat.client.tools.keys()

            async for node in chat.iter(prompt):
                if hasattr(node, "model_response"):
                    for part in node.model_response.parts:
                        if part.part_kind == "text":
                            logger.info(part.content)
                            result["messages"].append(
                                {"kind": part.part_kind, "text": part.content}
                            )
                        elif part.part_kind == "tool-call":
                            logger.info(
                                f"Tool {part.tool_name}({part.tool_call_id}): {part.args}"
                            )
                            result["messages"].append(
                                {
                                    "kind": part.part_kind,
                                    "tool": {
                                        "name": part.tool_name,
                                        "input": part.args_as_dict(),
                                    },
                                    "tool_call_id": part.tool_call_id,
                                }
                            )
                            tool_analysis.analyze_message(
                                result["messages"][-1], len(result["messages"]) - 1
                            )

                elif hasattr(node, "request"):
                    for part in node.request.parts:
                        if part.part_kind == "text":
                            result["messages"].append(
                                {"kind": part.part_kind, "text": part.content}
                            )
                        elif part.part_kind == "tool-return":
                            logger.info(
                                f"Tool returned {part.tool_name}({part.tool_call_id})"
                            )
                            logger.debug(
                                f"Tool result {part.tool_name}({part.tool_call_id}):\n{part.content}"
                            )
                            result["messages"].append(
                                {
                                    "kind": part.part_kind,
                                    "tool_name": part.tool_name,
                                    "content": part.content,
                                    "tool_call_id": part.tool_call_id,
                                }
                            )
                elif hasattr(node, "data"):
                    logger.info(f"Final result: {node.data.data}")
                    result["messages"].append(
                        {"kind": "final_result", "text": node.data.data}
                    )

        except KeyboardInterrupt:
            return None
        except Exception:
            logger.error(f"{model.slug} failed: {traceback.format_exc()}")
            return None

        return result

    async def run(
        self,
        prompt: str,
        check: str,
        expected_tools: List[str],
    ) -> Results:
        """Run evaluation across all models."""
        scores = []
        total_duration = timedelta(seconds=0)

        for model in self.models:
            start = datetime.now()
            tool_analysis = ToolAnalysis()

            logger.info(f"Evaluating model {model.slug}")
            result = await self.evaluate_model(model, prompt, tool_analysis)

            if result is None:
                continue

            duration = datetime.now() - start
            duration_seconds = duration.total_seconds()
            total_duration += duration

            result["duration_in_seconds"] = f"{duration_seconds}s"
            result["number_of_tools_used"] = str(tool_analysis.total_tool_calls)

            logger.info(f"Analyzing results of {model.slug}")
            agent = Chat(
                client=mcp_run.Client(
                    config=mcp_run.ClientConfig(profile=model.profile)
                ),
                model=model.name,
                ignore_tools=self.ignore_tools,
                result_type=ScoreModel,
                system_prompt=SYSTEM_PROMPT,
                result_retries=10,
            )

            res = await agent.send_message(f"""
<settings>
Current date and time: {datetime.now().isoformat()}
</settings>
<prompt>
{prompt}
</prompt>
<output>
{json.dumps(result)}
</output>
<check>{check}</check>
<expected-tools>{", ".join(expected_tools)}</expected-tools>
""")

            scores.append(
                Score(
                    score=res.data,
                    model=model.slug,
                    duration=duration_seconds,
                    tool_analysis=tool_analysis.tool_analysis,
                    redundant_tool_calls=tool_analysis.redundant_tool_calls,
                    tool_calls=tool_analysis.total_tool_calls,
                )
            )

        return Results(scores=scores, duration=total_duration.total_seconds())
