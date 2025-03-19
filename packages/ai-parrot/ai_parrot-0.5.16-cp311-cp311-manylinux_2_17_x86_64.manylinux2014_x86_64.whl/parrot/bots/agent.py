from pathlib import Path
from typing import List, Any, Union
import os
from datetime import datetime, timezone
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate
)
from langchain_core.retrievers import BaseRetriever
from langchain import hub
from langchain.callbacks.base import BaseCallbackHandler
from langchain.agents import (
    create_react_agent,
    create_openai_functions_agent,
    create_openai_tools_agent,
    create_tool_calling_agent
)
from langchain.agents.agent import (
    AgentExecutor,
    RunnableAgent,
    RunnableMultiActionAgent,
)
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.json.base import create_json_agent
from langchain_community.tools.json.tool import JsonSpec
from langchain_community.agent_toolkits.json.toolkit import JsonToolkit
from langchain_community.utilities import TextRequestsWrapper
# for exponential backoff
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from datamodel.typedefs import SafeDict
from datamodel.parsers.json import json_decoder  # noqa  pylint: disable=E0611
from navconfig.logging import logging
from .abstract import AbstractBot
from .prompts import AGENT_PROMPT
from ..models import AgentResponse
from ..tools import AbstractTool, SearchTool, MathTool, DuckDuckGoSearchTool


os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Hide TensorFlow logs if present
logging.getLogger("grpc").setLevel(logging.CRITICAL)

class BasicAgent(AbstractBot):
    """Represents an Agent in Navigator.

        Agents are chatbots that can access to Tools and execute commands.
        Each Agent has a name, a role, a goal, a backstory,
        and an optional language model (llm).

        These agents are designed to interact with structured and unstructured data sources.
    """
    def __init__(
        self,
        name: str = 'Agent',
        agent_type: str = 'zero_shot',
        llm: str = 'vertexai',
        tools: List[AbstractTool] = None,
        system_prompt: str = None,
        human_prompt: str = None,
        prompt_template: str = None,
        **kwargs
    ):
        super().__init__(
            name=name,
            llm=llm,
            system_prompt=system_prompt,
            human_prompt=human_prompt,
            **kwargs
        )
        self.agent = None
        self.agent_type = agent_type
        self._agent = None # Agent Executor
        self.prompt_template = prompt_template or AGENT_PROMPT
        self.tools = tools or self.default_tools(tools)
        if system_prompt:
            self.prompt_template = self.prompt_template.format_map(
                SafeDict(
                    system_prompt_base=system_prompt
                )
            )
        else:
            self.prompt_template = self.prompt_template.format_map(
                SafeDict(
                    system_prompt_base="""
                    Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
                    """
                )
            )
        self.prompt = self.define_prompt(self.prompt_template)
        ##  Logging:
        self.logger = logging.getLogger(
            f'{self.name}.Agent'
        )

    def default_tools(self, tools: list = None) -> List[AbstractTool]:
        ctools = [
            DuckDuckGoSearchTool(),
            SearchTool(),
            MathTool()
        ]
        if tools:
            ctools.extend(tools)
        return ctools

    def define_prompt(self, prompt, **kwargs):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        list_of_tools = ""
        for tool in self.tools:
            name = tool.name
            description = tool.description  # noqa  pylint: disable=E1101
            list_of_tools += f'- {name}: {description}\n'
        list_of_tools += "\n"
        final_prompt = prompt.format_map(
            SafeDict(
                today_date=now,
                list_of_tools=list_of_tools
            )
        )
        # Define a structured system message
        system_message = f"""
        Today is {now}. If an event is expected to have occurred before this date,
        assume that results exist and verify using a web search tool.

        If you call a tool and receive a valid answer, finalize your response immediately.
        Do NOT repeat the same tool call multiple times for the same question.
        """
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            ChatPromptTemplate.from_template(final_prompt)
        ])
        return chat_prompt.partial(
            tools=self.tools,
            tool_names=", ".join([tool.name for tool in self.tools]),
            name=self.name,
            **kwargs
        )

    def get_retriever_tool(
        self,
        retriever: BaseRetriever,
        name: str = 'vector_retriever',
        description: str = 'Search for information about a topic in a Vector Retriever.',
    ):
        return create_retriever_tool(
            name=name,
            description=description,
            retriever=retriever,
        )

    def runnable_json_agent(self, json_file: Union[str, Path], **kwargs):
        """
        Creates a JSON Agent using `create_json_agent`.

        This agent is designed to work with structured JSON input and output.

        Returns:
            RunnableMultiActionAgent: A JSON-based agent.

        ✅ Use Case: Best when dealing with structured JSON data and needing a predictable schema.
        """
        data = None
        if isinstance(json_file, str):
            data = json_file
        elif isinstance(json_file, Path):
            data = json_file.read_text()
        data = json_decoder(data)
        json_spec = JsonSpec(dict_= data, max_value_length=4000)
        json_toolkit = JsonToolkit(spec=json_spec)
        agent = create_json_agent(
            llm=self._llm,
            toolkit=json_toolkit,
            verbose=True,
            prompt=self.prompt,
        )
        return self.prompt | self._llm | agent

    def runnable_agent(self, **kwargs):
        """
        Creates a ZeroShot ReAct Agent.

        This agent uses reasoning and tool execution iteratively to generate responses.

        Returns:
            RunnableMultiActionAgent: A ReAct-based agent.

        ✅ Use Case: Best for decision-making and reasoning tasks where the agent must break problems down into multiple steps.

        """
        return RunnableMultiActionAgent(
            runnable = create_react_agent(
                self._llm,
                self.tools,
                prompt=self.prompt,
            ),  # type: ignore
            input_keys_arg=["input"],
            return_keys_arg=["output"],
            **kwargs
        )

    def function_calling_agent(self, **kwargs):
        """
        Creates a Function Calling Agent.

        This agent uses reasoning and tool execution iteratively to generate responses.

        Returns:
            RunnableMultiActionAgent: A ReAct-based agent.

        ✅ Use Case: Best for decision-making and reasoning tasks where the agent must break problems down into multiple steps.

        """
        return RunnableMultiActionAgent(
            runnable = create_tool_calling_agent(
                self._llm,
                self.tools,
                prompt=self.prompt,
            ),  # type: ignore
            input_keys_arg=["input"],
            return_keys_arg=["output"],
            **kwargs
        )

    def openai_agent(self, **kwargs):
        """
        Creates OpenAI-like task executor Agent.

        This agent uses reasoning and tool execution iteratively to generate responses.

        Returns:
            RunnableMultiActionAgent: A ReAct-based agent.

        ✅ Use Case: Best for decision-making and reasoning tasks where the agent must break problems down into multiple steps.

        """
        return RunnableMultiActionAgent(
            runnable = create_openai_functions_agent(
                self._llm,
                self.tools,
                prompt=self.prompt
            ),  # type: ignore
            input_keys_arg=["input"],
            return_keys_arg=["output"],
            **kwargs
        )

    def sql_agent(self, dsn: str, **kwargs):
        """
        Creates a SQL Agent.

        This agent is designed to work with SQL queries and databases.

        Returns:
            AgentExecutor: A SQL-based AgentExecutor.

        ✅ Use Case: Best for querying databases and working with SQL data.
        """
        db = SQLDatabase.from_uri(dsn)
        toolkit = SQLDatabaseToolkit(db=db, llm=self._llm)
        # prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
        return create_sql_agent(
            llm=self._llm,
            toolkit=toolkit,
            db=db,
            agent_type= "openai-tools",
            extra_tools=self.tools,
            max_iterations=5,
            handle_parsing_errors=True,
            verbose=True,
            prompt=self.prompt,
            agent_executor_kwargs = {"return_intermediate_steps": False}
        )

    def get_executor(
        self,
        agent: RunnableAgent,
        tools: list,
        verbose: bool = True,
        **kwargs
    ):
        """Create a new AgentExecutor.
        """
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            return_intermediate_steps=False,
            max_iterations=5,
            max_execution_time=360,
            handle_parsing_errors=True,
            # memory=self.memory,
            **kwargs,
        )

    def get_agent(self):
        return self.get_executor(self.agent, self.tools)

    async def configure(self, app=None) -> None:
        """Basic Configuration of Agent.
        """
        await super(BasicAgent, self).configure(app)
        # Configure LLM:
        self.configure_llm(use_chat=True)
        # Conversation History:
        self.memory = self.get_memory()
        # 1. Initialize the Agent (as the base for RunnableMultiActionAgent)
        if self.agent_type == 'zero_shot':
            self.agent = self.runnable_agent()
        elif self.agent_type == 'function_calling':
            self.agent = self.function_calling_agent()
        elif self.agent_type == 'openai':
            self.agent = self.openai_agent()
        # elif self.agent_type == 'json':
        #     self.agent = self.runnable_json_agent()
        # elif self.agent_type == 'sql':
        #     self.agent = self.sql_agent()
        else:
            self.agent = self.runnable_agent()
        # self.agent = self.openai_agent()
        # 2. Create Agent Executor - This is where we typically run the agent.
        #  While RunnableMultiActionAgent itself might be "runnable",
        #  we often use AgentExecutor to manage the agent's execution loop.
        self._agent = self.get_executor(self.agent, self.tools)

    async def question(
            self,
            question: str = None,
            **kwargs
    ):
        """question.

        Args:
            question (str): The question to ask the chatbot.
            memory (Any): The memory to use.

        Returns:
            Any: The response from the Agent.

        """
        # TODO: adding the vector-search to the agent
        input_question = {
            "input": question
        }
        result = self._agent.invoke(input_question)
        try:
            response = AgentResponse(question=question, **result)
            # response.response = self.as_markdown(
            #     response
            # )
            return response
        except Exception as e:
            self.logger.exception(
                f"Error on response: {e}"
            )
            raise

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def invoke(self, query: str):
        """invoke.

        Args:
            query (str): The query to ask the chatbot.

        Returns:
            str: The response from the chatbot.

        """
        input_question = {
            "input": query
        }
        result = await self._agent.ainvoke(input_question)
        try:
            response = AgentResponse(question=query, **result)
            try:
                return self.as_markdown(
                    response
                ), response
            except Exception as exc:
                self.logger.exception(
                    f"Error on response: {exc}"
                )
                return result.get('output', None), None
        except Exception as e:
            return result, e

    async def __aenter__(self):
        if not self._agent:
            await self.configure()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._agent = None
