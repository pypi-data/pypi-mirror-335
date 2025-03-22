"""Capabilities define hooks that can plug into the agent's pipeline."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import AsyncGenerator, TYPE_CHECKING

from flexai.message import Message, AIMessage, SystemMessage, MessageContent

if TYPE_CHECKING:
    from flexai.agent import Agent


@dataclass
class Capability(ABC):
    """Abstract base class for defining cognitive capabilities of an agent.

    Provides hooks to modify the agent's behavior at different stages of
    the conversation pipeline, allowing for customization of prompts,
    messages, and responses.
    """

    def setup(self, agent: Agent):
        """Perform any setup required by the capability.

        Args:
            agent: The agent that the capability is attached to.
        """
        pass

    async def modify_prompt(
        self, prompt: SystemMessage
    ) -> AsyncGenerator[MessageContent | SystemMessage, None]:
        """Modify the system prompt before it's sent to the LLM.

        Args:
            prompt: The current system prompt.

        Yields:
            Intermediate message chunks followed by the modified system prompt.
        """
        yield prompt

    async def modify_messages(
        self, messages: list[Message]
    ) -> AsyncGenerator[MessageContent | Message | list[Message], None]:
        """Modify the conversation messages before sending them to the LLM.

        This method can be used to add, remove, or alter messages in the
        conversation history before they are processed by the language model.

        Args:
            messages: The current conversation messages.

        Yields:
            Intermediate message chunks followed by the modified list of messages.
        """
        yield messages

    async def modify_response(
        self, messages: list[Message], response: AIMessage
    ) -> AsyncGenerator[MessageContent | AIMessage, None]:
        """Modify the AI-generated response before sending it to the user.

        This method allows for post-processing of the AI's response, which
        can include filtering, reformatting, or augmenting the content.

        Args:
            messages: The current conversation messages.
            response: The AI-generated response.

        Yields:
            Intermediate message chunks followed by the modified AI response.
        """
        yield response
