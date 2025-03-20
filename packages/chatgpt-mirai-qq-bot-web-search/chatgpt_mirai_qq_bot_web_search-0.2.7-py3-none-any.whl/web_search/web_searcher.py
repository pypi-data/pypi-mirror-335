from playwright.async_api import async_playwright
import trafilatura
import random
import time
import urllib.parse
import asyncio
import subprocess
import sys
from kirara_ai.logger import get_logger
import os
import re
import requests
import json
from kirara_ai.im.message import IMMessage
from kirara_ai.im.sender import ChatSender
import yaml
from datetime import datetime, date

logger = get_logger("WebSearchPlugin")
user_videoIds = {}
class WebSearcher:

    def __init__(self):

        self.playwright = None
        self.browser = None
        self.context = None
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.video_ids_file = os.path.join(current_dir, "douyin_video_ids.yaml")
        self.video_ids = self._load_video_ids()
        self.search_engines = {
            'bing': {
                'url': 'https://www.bing.com/search?q={}',
                'selectors': ['.b_algo', '#b_results .b_algo', 'main .b_algo'],
                'title_selector': 'h2',
                'link_selector': 'h2 a',
                'snippet_selector': '.b_caption p'
            },
            'google': {
                'url': 'https://www.google.com/search?q={}',
                'selectors': ['.MjjYud', 'div.g', 'div[data-hveid]'],
                'title_selector': 'h3.LC20lb',
                'link_selector': 'a[jsname="UWckNb"], div.yuRUbf a',
                'snippet_selector': 'div.VwiC3b'
            },
            'baidu': {
                'url': 'https://www.baidu.com/s?wd={}',
                'selectors': ['.result', '.result-op'],
                'title_selector': 'h3',
                'link_selector': 'h3 a',
                'snippet_selector': '.content-right_8Zs40'
            }
        }

    @classmethod
    async def create(cls):
        """创建 WebSearcher 实例的工厂方法"""
        self = cls()
        return self

    async def _ensure_initialized(self,proxy):
        """确保浏览器已初始化"""
        try:
            if self.context:
                return self.context
            self.playwright = await async_playwright().start()

            # 创建用户数据目录路径
            user_data_dir = os.path.join(os.path.expanduser("~"), ".playwright_user_data")+f'{random.randint(1, 1000000)}'
            os.makedirs(user_data_dir, exist_ok=True)

            # 合并所有选项到一个字典
            context_options = {
                'headless': True,
                'chromium_sandbox': False,
                'slow_mo': 50,  # 减慢操作速度，更像人类
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',  # 隐藏自动化控制痕迹
                    '--disable-features=IsolateOrigins,site-per-process',
                ],
                'ignore_default_args': ['--enable-automation'],  # 屏蔽自动化标志
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'locale': 'zh-CN',
                'timezone_id': 'Asia/Shanghai',
                'color_scheme': 'dark',  # 或 'light'，根据用户习惯
                'device_scale_factor': 1.75,  # 高DPI设备
                'has_touch': True,  # 支持触摸
                'is_mobile': False,
                'reduced_motion': 'no-preference'
            }

            # 如果是 Google 搜索，添加代理设置
            if proxy:
                context_options['proxy'] = {
                    'server': proxy
                }

            try:
                # 使用 launch_persistent_context 代替分开的 launch 和 new_context
                self.context = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    **context_options
                )

                self.browser = None  # 不再需要单独的browser引用

            except Exception as e:
                if "Executable doesn't exist" in str(e):
                    logger.info("Installing playwright browsers...")
                    process = subprocess.Popen(
                        [sys.executable, "-m", "playwright", "install", "chromium"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    stdout, stderr = process.communicate()
                    if process.returncode != 0:
                        raise RuntimeError(f"Failed to install playwright browsers: {stderr.decode()}")

                    # 重试使用 launch_persistent_context
                    self.context = await self.playwright.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        **context_options
                    )
                else:
                    raise

            # 注入脚本来伪装webdriver标记
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });

                // 防止 iframe 检测
                window.parent.document;

                // 防止检测到 Chrome Devtools 协议
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """)

            return self.context

        except Exception as e:
            logger.error(f"Failed to initialize WebSearcher: {e}")
            await self.close()
            raise

    async def simulate_human_scroll(self, page):
        """模拟人类滚动"""
        for _ in range(3):
            await page.mouse.wheel(0, random.randint(300, 700))

    async def get_webpage_content(self, url: str, timeout: int,context) -> str:
        """获取网页内容"""
        start_time = time.time()
        try:
            # 创建新标签页获取内容
            page = await context.new_page()
            try:
                # 设置更严格的资源加载策略
                await page.route("**/*", lambda route: route.abort()
                    if route.request.resource_type in ['image', 'stylesheet', 'font', 'media']
                    else route.continue_())

                # 使用 domcontentloaded 而不是 networkidle
                await page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)

                # 等待页面主要内容加载，但设置较短的超时时间
                try:
                    await page.wait_for_load_state('domcontentloaded', timeout=5000)
                except Exception as e:
                    logger.warning(f"Load state timeout for {url}, continuing anyway: {e}")

                await self.simulate_human_scroll(page)

                content = await page.content()
                text = trafilatura.extract(content)

                await page.close()
                logger.info(f"Content fetched - URL: {url} - Time: {time.time() - start_time:.2f}s")
                return text or ""
            except Exception as e:
                await page.close()
                logger.error(f"Failed to fetch content - URL: {url} - Error: {e}")
                return ""
        except Exception as e:
            logger.error(f"Failed to create page - URL: {url} - Error: {e}")
            return ""

    async def process_search_result(self, result, idx: int, timeout: int, fetch_content: bool, context, engine='bing'):
        """处理单个搜索结果"""
        try:
            engine_config = self.search_engines[engine]
            title_element = await result.query_selector(engine_config['title_selector'])
            link_element = await result.query_selector(engine_config['link_selector'])
            snippet_element = await result.query_selector(engine_config['snippet_selector'])

            if not title_element or not link_element:
                return None

            title = await title_element.inner_text()
            link = await link_element.get_attribute('href')

            # 对于百度搜索需要特殊处理链接
            if engine == 'baidu':
                try:
                    # 创建新页面来获取真实URL
                    new_page = await context.new_page()
                    await new_page.goto(link, wait_until='domcontentloaded', timeout=5000)
                    real_url = new_page.url
                    await new_page.close()
                    link = real_url
                except Exception as e:
                    logger.warning(f"Failed to get real URL from Baidu: {e}")

            snippet = await snippet_element.inner_text() if snippet_element else "无简介"

            if not link:
                return None

            result_text = f"[{idx+1}] {title}\nURL: {link}\n搜索简介: {snippet}"

            if fetch_content:

                content = await self.get_webpage_content(link, timeout,context)
                if content:
                    result_text += f"\n内容详情:\n{content}"

            return result_text

        except Exception as e:
            logger.error(f"Failed to process result {idx}: {e}")
            return None

    async def search(self, query: str, max_results: int = 3, timeout: int = 10, fetch_content: bool = True, engine: str = 'bing', proxy: str = None) -> str:
        """执行搜索"""
        if engine not in self.search_engines:
            return f"不支持的搜索引擎: {engine}"

        # 设置当前搜索引擎
        self.current_engine = engine
        context = await self._ensure_initialized(proxy)
        engine_config = self.search_engines[engine]
        search_start_time = time.time()
        page = None

        try:
            encoded_query = urllib.parse.quote(query)
            page = await context.new_page()

            # Google搜索特定处理
            await page.goto(
                                engine_config['url'].format(encoded_query),
                                wait_until='load',
                                timeout=timeout * 1000
                            )

            # 使用搜索引擎特定的选择器
            results = None

            # 对于Google，让页面有更多时间加载
            if engine == 'google':
                await self.simulate_human_scroll(page)

            timeout = 5000
            for selector in engine_config['selectors']:
                try:
                    logger.info(f"Trying selector: {selector}")
                    await page.wait_for_selector(selector, timeout=timeout)  # 增加等待时间
                    timeout = 500
                    results = await page.query_selector_all(selector)
                    if results and len(results) > 0:
                        logger.info(f"Found {len(results)} results with selector {selector}")
                        break
                except Exception as e:
                    logger.warning(f"Selector {selector} failed: {e}")
                    continue

            if not results:
                # 添加重试机制
                retry_count = 0
                while not results and retry_count < max_results:
                    logger.info(f"Retrying search, attempt {retry_count + 1}/{max_results}")
                    # 刷新页面重试
                    await page.reload(wait_until='load', timeout=timeout * 1000)
                    await self.simulate_human_scroll(page)

                    # 重新尝试所有选择器
                    timeout = 5000
                    for selector in engine_config['selectors']:
                        try:
                            logger.info(f"Retrying selector: {selector}")
                            await page.wait_for_selector(selector, timeout=timeout)
                            timeout = 500
                            results = await page.query_selector_all(selector)
                            if results and len(results) > 0:
                                logger.info(f"Found {len(results)} results with selector {selector} on retry {retry_count + 1}")
                                break
                        except Exception as e:
                            logger.warning(f"Selector {selector} failed on retry {retry_count + 1}: {e}")
                            continue

                    retry_count += 1


                # 如果所有重试都失败了，才返回错误
                if not results:
                    logger.error("No search results found after all retries")
                    return "搜索结果加载失败"

            logger.info(f"Found {len(results)} search results")

            tasks = []
            for idx, result in enumerate(results[:max_results]):
                tasks.append(self.process_search_result(result, idx, timeout, fetch_content, context, engine))

            detailed_results = []
            completed_results = await asyncio.gather(*tasks)

            for result in completed_results:
                if result:
                    detailed_results.append(result)

            total_time = time.time() - search_start_time
            results = "\n---\n".join(detailed_results) if detailed_results else "未找到相关结果"
            logger.info(f"Search completed - Query: {query} - Time: {total_time:.2f}s - Found {len(detailed_results)} valid results")
            return results

        except Exception as e:
            logger.error(f"Search failed - Query: {query} - Error: {e}", exc_info=True)
            return f"搜索失败: {str(e)}"
        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.error(f"Error closing page: {e}")

    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

    def _load_video_ids(self):
        """从YAML文件加载视频ID记录"""
        try:
            today = str(date.today())
            if os.path.exists(self.video_ids_file):
                with open(self.video_ids_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    # 检查是否是今天的数据
                    if data.get('date') == today:
                        return data.get('video_ids', {})

            # 如果文件不存在、数据为空或日期不是今天，创建新的空记录
            empty_data = {
                'date': today,
                'video_ids': {}
            }
            with open(self.video_ids_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(empty_data, f, allow_unicode=True)
            return empty_data['video_ids']
        except Exception as e:
            logger.error(f"Failed to load video IDs: {e}")
            return {}

    def _save_video_ids(self):
        """保存视频ID记录到YAML文件"""
        try:
            data = {
                'date': str(date.today()),
                'video_ids': self.video_ids
            }
            # 确保目录存在
            os.makedirs(os.path.dirname(self.video_ids_file), exist_ok=True)
            # 使用 'w' 模式覆盖写入文件
            with open(self.video_ids_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"Failed to save video IDs: {e}")

    async def search_douyin_videos(self, keyword: str, count: int = 5, timeout: int = 10, proxy: str = None, sender: str = None) -> str:
        """搜索抖音视频"""
        context = await self._ensure_initialized(proxy)
        page = None

        if not sender:
            return "需要提供发送者ID"

        if sender not in self.video_ids:
            self.video_ids[sender] = []

        try:
            # 构建搜索URL
            search_url = f'https://www.douyin.com/search/{urllib.parse.quote(keyword)}'
            page = await context.new_page()

            # 设置User-Agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

            # 访问搜索页面并等待包含waterfall_item_的内容出现
            await page.goto(search_url, wait_until='domcontentloaded')

            # 等待页面中出现waterfall_item_字符串
            await page.wait_for_function('''
                () => document.documentElement.innerHTML.includes('waterfall_item_')
            ''', timeout=timeout * 1000)

            # 获取ttwid
            url = "https://ttwid.bytedance.com/ttwid/union/register/"
            ttjson = {"region": "cn", "aid": 1768, "needFid": "false", "service": "www.ixigua.com",
                        "migrate_info": {"ticket": "", "source": "node"}, "cbUrlProtocol": "https", "union": "true"}
            ttresponse = requests.post(url, json=ttjson)
            tt = ttresponse.cookies.get_dict()['ttwid']

            video_links = []
            videoCount = 0
            max_scroll_attempts = 10  # 最大滚动尝试次数
            scroll_attempt = 0
            while videoCount < count and scroll_attempt < max_scroll_attempts:
                # 提取视频ID
                video_elements = await page.query_selector_all('div[id^="waterfall_item_"]')

                # 处理当前页面上的视频
                for i, element in enumerate(video_elements):
                    if videoCount >= count:
                        break

                    # 获取元素的id属性
                    div_id = await element.get_attribute('id')
                    video_id = div_id.replace('waterfall_item_', '')
                    if video_id not in self.video_ids[sender]:
                        if video_id.isdigit():  # 确保是数字ID
                            url = f'https://www.douyin.com/video/{video_id}'
                            try:
                                headers = {
                                    "referer": "https://www.douyin.com/",
                                    "user-agent": "Mozilla/5.0 (Linux; Android 12; 2210132C Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36",
                                    "cookie": "ttwid=" + tt
                                }
                                video_url = url
                                aweme_id = re.findall('video/(\d+)', url)[0]
                                url1 = f"https://www.iesdouyin.com/share/video/{aweme_id}"
                                resp1 = requests.get(url1, headers=headers).text.encode('gbk', errors='ignore').decode('gbk')
                                json_data = resp1.split("window._ROUTER_DATA = ")[1].split("</script>")[0]
                                resp1 = json.loads(json_data.encode('gbk', errors='ignore').decode('gbk'))
                                video_url = resp1["loaderData"]["video_(id)/page"]["videoInfoRes"]["item_list"][0]["video"]["play_addr"]["url_list"][0]
                                video_url = video_url.replace("playwm", "play").replace("720p", "1080p")
                                imgresponse = requests.get(video_url, allow_redirects=False)
                                new_url = imgresponse.headers.get('Location')
                                if new_url:  # 只有获取到重定向地址才添加
                                    logger.debug(new_url)
                                    video_links.append(f'[{videoCount+1}] {new_url}')
                                    videoCount += 1
                                    self.video_ids[sender].append(video_id)
                                    self._save_video_ids()  # 每添加一个视频就保存一次
                            except Exception as e:
                                continue

                # 如果还没有获取够视频，继续滚动加载
                if videoCount < count:
                    # 滚动到页面底部
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    await asyncio.sleep(2)  # 等待新内容加载
                    scroll_attempt += 1
                if scroll_attempt == 10:
                    self.video_ids[sender] = []
                    self._save_video_ids()

            return ("视频url地址:\n"+"\n".join(video_links)) if video_links else "未找到视频"

        except Exception as e:
            logger.error(f"抖音视频搜索失败 - 关键词: {keyword} - 错误: {e}", exc_info=True)
            return f"搜索失败: {str(e)}"
        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.error(f"关闭页面错误: {e}")
