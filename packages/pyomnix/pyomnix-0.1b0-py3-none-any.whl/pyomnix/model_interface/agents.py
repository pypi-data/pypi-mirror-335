"""
This module contains the agents for the model interface.
"""

from typing import Any, Dict, List, Optional, Generator, Union
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.language_models import BaseChatModel

from .models import Models, ChatRequest, ChatMessages, ChatMessageDict
MessagesState = ChatMessages

#############
# ChatBot
#############

class ChatBot():
    """
    A chatbot that can be used to chat with a model.
    
    This class implements a chatbot using LangChain's components, providing a structured
    way to interact with language models. It supports conversation history management,
    tool usage, and customizable chat behaviors.

    Attributes:
        model: The language model to use for chat interactions
        memory: List of messages representing the conversation history
        tools: Optional list of tools the chatbot can use
        system_message: The system message that defines the chatbot's behavior
        max_iterations: Maximum number of iterations for tool usage
        verbose: Whether to print debug information
    """

    model: BaseChatModel = Field(description="The language model to use for chat")
    memory: List[AnyMessage] = Field(default_factory=list, description="Conversation history")
    tools: Optional[List[Tool]] = Field(default=None, description="Tools available to the chatbot")
    system_message: str = Field(
        default="You are a helpful AI assistant.",
        description="System message defining chatbot behavior"
    )
    max_iterations: int = Field(default=5, description="Maximum iterations for tool usage")
    verbose: bool = Field(default=False, description="Whether to print debug information")

    def __init__(self, provider_api: str | list[str], model: str | list[str], **kwargs) -> None:
        """
        Initialize the ChatBot with the given configuration.

        Args:
            provider_api: The provider API identifier or list of identifiers
            model: The model name or list of model names
            **kwargs: Additional configuration parameters for the chatbot
                      Optional keys: memory, tools, system_message, max_iterations, verbose
        """
        super(BaseModel, self).__init__()
        super(RawModels, self).__init__(provider_api)
        self._initialize_memory()
        self._setup_agent()

    def _initialize_memory(self) -> None:
        """
        Initialize the conversation memory with the system message.
        """
        if not self.memory:
            self.memory = [SystemMessage(content=self.system_message)]

    def _setup_agent(self) -> None:
        """
        Set up the agent executor if tools are provided.
        """
        if self.tools:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_message),
                ("human", "{input}"),
                ("assistant", "{agent_scratchpad}")
            ])
            
            self.agent = create_react_agent(self.model, self.tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                max_iterations=self.max_iterations,
                verbose=self.verbose
            )

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.

        Args:
            role: The role of the message sender ('user', 'assistant', or 'system')
            content: The content of the message
        """
        message_dict = ChatMessageDict(role=role, content=content)
        self.memory.append(message_dict.to_langchain_message())

    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history in a structured format.

        Returns:
            List[Dict[str, str]]: List of messages with role and content
        """
        return [
            {"role": msg.__class__.__name__.replace("Message", "").lower(), 
             "content": msg.content}
            for msg in self.memory
        ]

    async def agenerate_response(self, user_input: str) -> str:
        """
        Asynchronously generate a response to the user input.

        Args:
            user_input: The user's input message

        Returns:
            str: The generated response
        """
        self.add_message("user", user_input)

        if self.tools:
            response = await self.agent_executor.ainvoke(
                {"input": user_input, "chat_history": self.memory[:-1]}
            )
            response_text = response["output"]
        else:
            response = await self.model.agenerate([self.memory])
            response_text = response.generations[0][0].text

        self.add_message("assistant", response_text)
        return response_text

    def generate_response(self, user_input: str) -> str:
        """
        Synchronously generate a response to the user input.

        Args:
            user_input: The user's input message

        Returns:
            str: The generated response
        """
        self.add_message("user", user_input)

        if self.tools:
            response = self.agent_executor.invoke(
                {"input": user_input, "chat_history": self.memory[:-1]}
            )
            response_text = response["output"]
        else:
            response = self.model.generate([self.memory])
            response_text = response.generations[0][0].text

        self.add_message("assistant", response_text)
        return response_text

    def clear_memory(self) -> None:
        """
        Clear the conversation history, keeping only the system message.
        """
        self._initialize_memory()

    def save_conversation(self, file_path: str) -> None:
        """
        Save the conversation history to a file.

        Args:
            file_path: Path to save the conversation history
        """
        chat_history = self.get_chat_history()
        with open(file_path, 'w', encoding='utf-8') as f:
            for message in chat_history:
                f.write(f"{message['role']}: {message['content']}\n")

    def load_conversation(self, file_path: str) -> None:
        """
        Load a conversation history from a file.

        Args:
            file_path: Path to load the conversation history from
        """
        self.clear_memory()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                role, content = line.strip().split(': ', 1)
                self.add_message(role, content)