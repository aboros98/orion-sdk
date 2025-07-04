from .base_node import BaseNode
from orion.agent_core.models import ToolCall
import asyncio
import logging


# Templates and prompts used in this module
DEFAULT_CLARIFICATION_PROMPT_TEMPLATE = """Please provide clarification for the following request:

{original_input}"""

ENHANCED_OUTPUT_TEMPLATE = """Original request: {original_input}

User clarification: {user_clarification}"""

CANCELLED_OUTPUT_TEMPLATE = """Original request: {original_input}

Status: Clarification {status}"""

MISSING_CONTEXT_CLARIFICATION_PROMPT = """The system has requested clarification, but no original context was provided. Please provide the necessary information:"""

USER_INPUT_PROMPT = "💬 Your response: "

logger = logging.getLogger(__name__)


class HumanInTheLoopNode(BaseNode):
    """
    A node that asks for human clarification during workflow execution.
    The compute function for this node is predefined.

    This node:
    - Expects a ToolCall input with 'original_input' and 'clarification_prompt'.
    - Presents the clarification prompt to the user.
    - Waits for user input via the console.
    - Concatenates the clarification with the original input.
    - Returns the enhanced input for further processing.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a human-in-the-loop node.

        Args:
            name: Unique identifier for the node.
        """
        # BaseNode requires a callable, but the logic is in compute.
        # So we provide a no-op lambda.
        super().__init__(name, lambda: None)

    async def _wait_for_user_input(self, clarification_prompt: str) -> str:
        """
        Wait for user input with the given clarification prompt.
        This is the core interaction mechanism.
        """
        # Show only the clarification prompt provided by the orchestrator
        print(f"\n{clarification_prompt}\n")

        try:
            loop = asyncio.get_event_loop()
            user_input = await loop.run_in_executor(None, input, USER_INPUT_PROMPT)

            print(f"\n✅ Got it! You said: {user_input}")

            return user_input.strip()

        except KeyboardInterrupt:
            print("\n❌ User cancelled clarification request")
            return "[CANCELLED]"
        except Exception as e:
            logger.error(f"Error getting user input: {e}")
            return f"[ERROR: {str(e)}]"

    async def compute(self, input_data: ToolCall, *args, **kwargs) -> str:
        """
        Execute the human-in-the-loop clarification process.

        Args:
            input_data: A ToolCall object from an orchestrator.
                The arguments should contain:
                - 'original_input': The input needing clarification.
                - 'clarification_prompt': A prompt to show the user.

        Returns:
            An enhanced input string combining the original request with user clarification.

        Raises:
            TypeError: If input_data is not a ToolCall.
        """
        logger.info(f"HumanInTheLoopNode '{self.name}' processing clarification request")

        if not isinstance(input_data, ToolCall):
            raise TypeError(f"HumanInTheLoopNode expects a ToolCall as input, but received {type(input_data)}")

        try:
            # Extract prompts from ToolCall arguments
            args = input_data.arguments
            original_input = args.get("original_input", args.get("input", ""))
            clarification_prompt = args.get(
                "clarification_prompt", DEFAULT_CLARIFICATION_PROMPT_TEMPLATE.format(original_input=original_input)
            )

            if not original_input:
                logger.warning(f"HumanInTheLoopNode '{self.name}' received empty original_input")
                clarification_prompt = MISSING_CONTEXT_CLARIFICATION_PROMPT

            # Get user clarification
            user_clarification = await self._wait_for_user_input(clarification_prompt)

            # Create enhanced output
            if user_clarification.startswith("[CANCELLED]") or user_clarification.startswith("[ERROR"):
                enhanced_output = CANCELLED_OUTPUT_TEMPLATE.format(
                    original_input=original_input, status=user_clarification
                )
            else:
                enhanced_output = ENHANCED_OUTPUT_TEMPLATE.format(
                    original_input=original_input, user_clarification=user_clarification
                )

            logger.info(f"HumanInTheLoopNode '{self.name}' completed clarification successfully")

            return enhanced_output

        except Exception as e:
            logger.error(f"HumanInTheLoopNode '{self.name}' failed to process clarification: {e}")
            raise Exception(f"Human-in-the-loop clarification failed: {e}")
