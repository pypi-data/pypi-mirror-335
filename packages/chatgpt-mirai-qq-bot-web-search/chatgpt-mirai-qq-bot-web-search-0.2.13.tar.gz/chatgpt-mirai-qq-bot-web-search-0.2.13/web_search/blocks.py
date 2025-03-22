from typing import Any, Dict, List, Optional,Annotated
import asyncio
from kirara_ai.workflow.core.block import Block, Input, Output, ParamMeta
from .web_searcher import WebSearcher
from .config import WebSearchConfig
from kirara_ai.llm.format.message import LLMChatMessage
from kirara_ai.llm.format.response import LLMChatResponse
from kirara_ai.ioc.container import DependencyContainer
import re
from kirara_ai.im.message import IMMessage
from kirara_ai.im.sender import ChatSender, ChatType
def get_options_provider(container: DependencyContainer, block: Block) -> List[str]:
    return ["bing", "google", "baidu"]
class WebSearchBlock(Block):
    """Web搜索Block"""
    name = "web_search"
    inputs = {
        "llm_resp": Input(name="llm_resp",label="LLM 响应", data_type=LLMChatResponse, description="搜索关键词")
    }

    outputs = {
        "results": Output(name="results",label="搜索结果",data_type= str, description="搜索结果")
    }

    def __init__(self, name: str = None, max_results: Optional[int] = 3, timeout: Optional[int] = 10, fetch_content: Optional[bool] = True
    ,engine: Annotated[Optional[str],ParamMeta(label="搜索引擎", description="要使用的搜索引擎", options_provider=get_options_provider),] = "bing", proxy: str = None,):
        super().__init__(name)
        self.searcher = None
        self.config = WebSearchConfig()
        self.max_results = max_results
        self.timeout = timeout
        self.fetch_content = fetch_content
        self.engine=engine
        self.proxy = proxy

    def _ensure_searcher(self):
        """同步方式初始化searcher"""
        if not self.searcher:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # 如果在新线程中没有事件循环，则创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            self.searcher = loop.run_until_complete(WebSearcher.create())

    def execute(self, **kwargs) -> Dict[str, Any]:
        llmResponse = kwargs["llm_resp"]

        query = llmResponse.choices[0].message.content if llmResponse.choices else ""
        if query == "" or query.startswith("无"):
            return {"results": ""}
        max_results = self.max_results
        timeout = self.timeout
        fetch_content = self.fetch_content
        self._ensure_searcher()

        try:
            # 在新线程中创建事件循环
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            results = loop.run_until_complete(
                self.searcher.search(
                    query=query,
                    max_results=max_results,
                    timeout=timeout,
                    fetch_content=fetch_content,
                    engine=self.engine,
                    proxy = self.proxy,
                )
            )
            return {"results": "\n以下是联网搜索的结果:\n-- 搜索结果开始 --\n"+results+"\n-- 搜索结果结束 --\n"}
        except Exception as e:
            print(e)
            return {"results": f"搜索失败: {str(e)}"}
class WebSearchByKeywordBlock(Block):
    """Web搜索Block"""
    name = "web_search_by_keyword"
    description = "网络搜索，通过关键词进行网络搜索"

    inputs = {
        "keyword": Input(name="keyword",label="搜索关键字", data_type=str, description="搜索关键词")
    }

    outputs = {
        "results": Output(name="results",label="搜索结果",data_type= str, description="搜索结果")
    }

    def __init__(self, name: str = None, max_results: Optional[int] = 3, timeout: Optional[int] = 10, fetch_content: Optional[bool] = True
    ,engine: Annotated[Optional[str],ParamMeta(label="搜索引擎", description="要使用的搜索引擎", options_provider=get_options_provider),] = "bing", proxy: str = None,):
        super().__init__(name)
        self.searcher = None
        self.config = WebSearchConfig()
        self.max_results = max_results
        self.timeout = timeout
        self.fetch_content = fetch_content
        self.engine=engine
        self.proxy = proxy

    def _ensure_searcher(self):
        """同步方式初始化searcher"""
        if not self.searcher:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # 如果在新线程中没有事件循环，则创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            self.searcher = loop.run_until_complete(WebSearcher.create())

    def execute(self, **kwargs) -> Dict[str, Any]:
        query = kwargs["keyword"]

        if query == "" or query.startswith("无"):
            return {"results": ""}
        max_results = self.max_results
        timeout = self.timeout
        fetch_content = self.fetch_content
        self._ensure_searcher()

        try:
            # 在新线程中创建事件循环
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            results = loop.run_until_complete(
                self.searcher.search(
                    query=query,
                    max_results=max_results,
                    timeout=timeout,
                    fetch_content=fetch_content,
                    engine=self.engine,
                    proxy = self.proxy,
                )
            )
            return {"results": "\n以下是联网搜索的结果:\n-- 搜索结果开始 --"+results+"\n-- 搜索结果结束 --"}
        except Exception as e:
            print(e)
            return {"results": f"搜索失败: {str(e)}"}

class AppendSystemPromptBlock(Block):
    """将搜索结果附加到系统提示的Block"""
    name = "append_system_prompt"

    inputs = {
        "results": Input(name="results",label="工具结果", data_type=str, description ="搜索结果"),
        "messages": Input(name="messages",label="LLM 响应", data_type=List[LLMChatMessage],description = "消息列表")
    }

    outputs = {
        "messages": Output(name="messages", label="拼装后的 llm 响应",data_type=List[LLMChatMessage], description = "更新后的消息列表")
    }

    def execute(self, **kwargs) -> Dict[str, Any]:
        results = kwargs["results"]
        messages: List[LLMChatMessage] = kwargs["messages"]

        if messages and len(messages) > 0 and results and isinstance(messages[0].content,str):
            # 在第一条消息内容后面附加搜索结果
            messages[0].content = messages[0].content + f"{results}"

        return {"messages": messages}

class DouyinVideoSearchBlock(Block):
    """抖音视频搜索Block"""
    name = "douyin_video_search"
    description = "通过关键词搜索抖音视频"
    container: DependencyContainer
    inputs = {
        "keyword": Input(name="keyword", label="搜索关键字", data_type=str, description="搜索关键词"),
        "count": Input(name="count", label="视频数量", data_type=int, description="需要获取的视频数量")
    }

    outputs = {
        "results": Output(name="results", label="搜索结果", data_type=str, description="视频链接列表")
    }

    def __init__(self, name: str = None, timeout: Optional[int] = 10, proxy: str = None):
        super().__init__(name)
        self.searcher = None
        self.config = WebSearchConfig()
        self.timeout = timeout
        self.proxy = proxy

    def _ensure_searcher(self):
        """同步方式初始化searcher"""
        if not self.searcher:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            self.searcher = loop.run_until_complete(WebSearcher.create())

    def execute(self, **kwargs) -> Dict[str, Any]:
        keyword = kwargs["keyword"]
        count = kwargs["count"]

        if not keyword:
            return {"results": ""}

        self._ensure_searcher()

        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            sender = self.container.resolve(IMMessage).sender
            results = loop.run_until_complete(
                self.searcher.search_douyin_videos(
                    keyword=keyword,
                    count=count,
                    timeout=self.timeout,
                    proxy=self.proxy,
                    sender = sender.group_id if sender.chat_type == ChatType.GROUP else sender.user_id
                )
            )
            return {"results": f"\n以下是抖音视频搜索结果:\n{results}"}
        except Exception as e:
            print(e)
            return {"results": f"搜索失败: {str(e)}"}

