from abc import abstractmethod, ABC

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from typing_extensions import List

from .schema import BaseState


class InvokeComponentBase(ABC):
    """base class for invokable component"""

    llm: BaseChatModel

    tools: List[BaseTool]

    prompt_template: ChatPromptTemplate

    def __init__(self, llm: BaseChatModel, tools: List[BaseTool], prompt_template: ChatPromptTemplate, **kwargs):
        assert llm is not None
        assert tools is not None
        assert len(tools) > 0
        assert prompt_template is not None

        self.llm = llm
        self.tools = tools
        self.prompt_template = prompt_template

    @abstractmethod
    def invoke(self, state: BaseState):
        raise NotImplemented

    @classmethod
    @abstractmethod
    def create(cls, llm: BaseChatModel, tools: List[BaseTool], **kwargs):
        raise NotImplemented

    @property
    def llm_callable_with_tools(self):
        return self.prompt_template | self.llm.bind_tools(tools=self.tools)

    @property
    def llm_callable(self):
        return self.prompt_template | self.llm
