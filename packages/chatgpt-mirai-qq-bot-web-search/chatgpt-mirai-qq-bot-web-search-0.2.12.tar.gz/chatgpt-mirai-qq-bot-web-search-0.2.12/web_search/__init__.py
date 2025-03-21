from typing import Dict, Any, List
import asyncio
from kirara_ai.plugin_manager.plugin import Plugin
import subprocess
import sys
import sys
from kirara_ai.logger import get_logger
from .config import WebSearchConfig
from .web_searcher import WebSearcher
from dataclasses import dataclass
from kirara_ai.workflow.core.block import BlockRegistry
from .blocks import WebSearchBlock,WebSearchByKeywordBlock, DouyinVideoSearchBlock
from .blocks import AppendSystemPromptBlock
from kirara_ai.ioc.inject import Inject
from kirara_ai.ioc.container import DependencyContainer
from kirara_ai.workflow.core.workflow.builder import WorkflowBuilder
from kirara_ai.workflow.core.workflow.registry import WorkflowRegistry
logger = get_logger("WebSearch")
import importlib.resources
import os
from pathlib import Path
class WebSearchPlugin(Plugin):
    def __init__(self, block_registry: BlockRegistry , container: DependencyContainer):
        super().__init__()
        self.web_search_config = WebSearchConfig()
        self.searcher = None
        self.block_registry = block_registry
        self.workflow_registry = container.resolve(WorkflowRegistry)
        self.container=container
    def on_load(self):
        logger.info("WebSearchPlugin loading")

        try:
            # 运行检查命令
            result = subprocess.run(['playwright', 'install', 'chromium', '--dry-run'],
                                  capture_output=True,
                                  text=True)
            # 如果命令执行成功且输出中包含已安装的信息
            if "is already installed" not in result.stdout:
                logger.info("Installing playwright browsers...")
                process = subprocess.Popen(
                    [sys.executable, "-m", "playwright", "install", "chromium"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                if process.returncode != 0:
                    logger.error(f"Failed to install playwright browsers: {stderr}")
                    raise RuntimeError(f"Failed to install playwright browsers: {stderr}")
        except Exception as e:
            logger.info("Installing playwright browsers...")
            process = subprocess.Popen(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                logger.error(f"Failed to install playwright browsers: {stderr}")
                raise RuntimeError(f"Failed to install playwright browsers: {stderr}")
        # 注册Block
        try:
            self.block_registry.register("web_search", "search", WebSearchBlock)
            self.block_registry.register("web_search_by_keyword", "search", WebSearchByKeywordBlock)
            self.block_registry.register("douyin_video_search", "search", DouyinVideoSearchBlock)
        except Exception as e:
            logger.warning(f"WebSearchPlugin failed: {e}")
        try:
            self.block_registry.register("append_systemPrompt", "internal", AppendSystemPromptBlock)
        except Exception as e:
            logger.warning(f"WebSearchPlugin failed: {e}")
        try:
            # 获取当前文件的绝对路径
            with importlib.resources.path('web_search', '__init__.py') as p:
                package_path = p.parent
                example_dir = package_path / 'example'

                # 确保目录存在
                if not example_dir.exists():
                    raise FileNotFoundError(f"Example directory not found at {example_dir}")

                # 获取所有yaml文件
                yaml_files = list(example_dir.glob('*.yaml')) + list(example_dir.glob('*.yml'))

                for yaml in yaml_files:
                    logger.info(yaml)
                    self.workflow_registry.register("chat", yaml.stem, WorkflowBuilder.load_from_yaml(os.path.join(example_dir, yaml), self.container))
        except Exception as e:
            try:
                current_file = os.path.abspath(__file__)

                # 获取当前文件所在目录
                parent_dir = os.path.dirname(current_file)

                # 构建 example 目录的路径
                example_dir = os.path.join(parent_dir, 'example')
                # 获取 example 目录下所有的 yaml 文件
                yaml_files = [f for f in os.listdir(example_dir) if f.endswith('.yaml') or f.endswith('.yml')]

                for yaml in yaml_files:
                    logger.info(os.path.join(example_dir, yaml))
                    self.workflow_registry.register("search", "roleplayWithWebSearch", WorkflowBuilder.load_from_yaml(os.path.join(example_dir, yaml), self.container))
            except Exception as e:
                logger.warning(f"workflow_registry failed: {e}")

        @dataclass
        class WebSearchEvent:
            """Web搜索事件"""
            query: str

        async def handle_web_search(event: WebSearchEvent):
            """处理web搜索事件"""
            if not self.searcher:
                await self._initialize_searcher()
            return await self.searcher.search(
                event.query,
                max_results=self.web_search_config.max_results,
                timeout=self.web_search_config.timeout,
                fetch_content=self.web_search_config.fetch_content
            )
        try:
            self.event_bus.register(WebSearchEvent, handle_web_search)
        except Exception as e:
            logger.warning(f"WebSearchPlugin failed: {e}")

    def on_start(self):
        logger.info("WebSearchPlugin started")

    def on_stop(self):
        if self.searcher:
            asyncio.create_task(self.searcher.close())

        logger.info("WebSearchPlugin stopped")

    async def _initialize_searcher(self):
        """初始化搜索器"""
        if self.searcher is None:
            self.searcher = await WebSearcher.create()

