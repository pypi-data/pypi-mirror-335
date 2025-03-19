from typing import Any, Dict, List, Optional,Annotated
from kirara_ai.workflow.core.block import Block, Input, Output, ParamMeta

from kirara_ai.im.message import IMMessage, TextMessage, ImageMessage
from kirara_ai.im.sender import ChatSender
from .api_collection import ApiCollection
import asyncio
from kirara_ai.logger import get_logger
from kirara_ai.ioc.container import DependencyContainer
import os
import yaml
from kirara_ai.im.message import IMMessage
from kirara_ai.im.sender import ChatSender, ChatType

class WeatherSearchBlock(Block):
    """图片生成Block"""
    name = "weather_search"
    description = "查询天气"

    inputs = {
        "city": Input(name="city", label="城市名", data_type=str, description="城市名"),
    }

    outputs = {
        "results": Output(name="results", label="天气结果", data_type=str, description="天气结果")
    }

    def __init__(
        self,
        name: str = None,
    ):
        super().__init__(name)

        self.generator = ApiCollection()

    def execute(self, city:str) -> Dict[str, Any]:
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            results = loop.run_until_complete(
                self.generator.weacherSearch(
                    city=city,
                )
            )

            return {"results": results}
        except Exception as e:
            return {"results": f"生成失败: {str(e)}"}

class RandomGirlVideoBlock(Block):
    """随机美女视频 Block"""
    name = "random_girl_video"
    description = "随机获取1个美女视频，可重复调用获取多个"

    inputs = {}  # 不需要输入参数

    outputs = {
        "video_url": Output(name="video_url", label="视频链接", data_type=str, description="视频直链地址")
    }

    def __init__(
        self,
        name: str = None,
    ):
        super().__init__(name)
        self.generator = ApiCollection()

    def execute(self) -> Dict[str, Any]:
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            video_url = loop.run_until_complete(
                self.generator.get_random_girl_video()
            )

            # 格式化输出字符串
            return {"video_url": video_url}
        except Exception as e:
            return {"video_url": f"获取视频失败: {str(e)}"}
class RandomCosplayBlock(Block):
    """随机Cosplay图片 Block"""
    name = "random_cosplay"
    description = "获取随机cosplay图片"

    inputs = {
        "count": Input(name="count", label="图片数量", data_type=int, description="返回的图片数量", default=5)
    }

    outputs = {
        "image_info": Output(name="image_urls", label="图片信息", data_type=str, description="图片信息字符串")
    }

    def __init__(
        self,
        name: str = None,
    ):
        super().__init__(name)
        self.generator = ApiCollection()


    def execute(self, count: int = 5) -> Dict[str, Any]:
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            image_info = loop.run_until_complete(
                self.generator.get_random_cosplay(count=count)
            )

            # 格式化输出字符串
            formatted_info = f"标题: {image_info['Title']}\n图片链接:\n" + "\n".join(image_info['data'])
            print(formatted_info)
            return {"image_info": formatted_info}
        except Exception as e:
            return {"image_info": f"获取图片失败: {str(e)}"}

class RandomEmojiBlock(Block):
    """随机表情包 Block"""
    name = "random_emoji"
    description = "随机获取1个表情包，可重复调用获取多个"

    inputs = {}  # 不需要输入参数

    outputs = {
        "image_url": Output(name="image_url", label="图片链接", data_type=str, description="表情包图片直链地址")
    }

    def __init__(
        self,
        name: str = None,
    ):
        super().__init__(name)
        self.generator = ApiCollection()

    def execute(self) -> Dict[str, Any]:
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            image_url = loop.run_until_complete(
                self.generator.get_random_emoji()
            )

            return {"image_url": image_url}
        except Exception as e:
            return {"image_url": f"获取表情包失败: {str(e)}"}

class SougouImageSearchBlock(Block):
    """搜狗搜图 Block"""
    name = "sougou_image_search"
    description = "搜狗搜索1个图片，要求多张时需要重复调用多次"

    inputs = {
        "keyword": Input(name="keyword", label="关键词", data_type=str, description="搜索关键词")
    }

    outputs = {
        "image_url": Output(name="image_url", label="图片链接", data_type=str, description="搜索到的图片直链地址")
    }

    def __init__(
        self,
        name: str = None,
    ):
        super().__init__(name)
        self.generator = ApiCollection()

    def execute(self, keyword: str) -> Dict[str, Any]:
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            image_url = loop.run_until_complete(
                self.generator.get_sougou_image(keyword=keyword)
            )

            return {"image_url": image_url}
        except Exception as e:
            return {"image_url": f"搜图失败: {str(e)}"}

class CutOffPrefix(Block):
    """截断前缀 Block"""
    name = "cut_off_prefix"
    description = "截断前缀，用于</think>或者A:截断"
    from kirara_ai.llm.format.response import LLMChatResponse
    inputs = {"req": Output("resp", "LLM 对话响应", LLMChatResponse, "LLM 对话响应")}

    outputs = {"resp": Output("resp", "LLM 对话响应", LLMChatResponse, "LLM 对话响应")}

    def __init__(
        self,
        name: str = None,
        split: str = "A:",
    ):
        super().__init__(name)
        self.split = split

    def execute(self, req: LLMChatResponse) -> Dict[str, Any]:
        try:
            messages = req.choices[0].message.content.split(self.split)
            out = messages[1] if len(messages)>1 else messages[0]
            req.choices[0].message.content = out
            return {"resp": req}
        except Exception as e:
            return {"resp": req}

# ... existing code ...

class BilibiliRexBlock(Block):
    """B站链接解析 Block"""
    name = "bilibili_rex"
    description = "解析B站链接，获取视频信息"

    inputs = {
        "url": Input(name="url", label="B站链接", data_type=str, description="B站视频链接")
    }

    outputs = {
        "info": Output(name="info", label="视频信息", data_type=str, description="解析后的视频信息")
    }

    def __init__(
        self,
        name: str = None,
    ):
        super().__init__(name)
        self.generator = ApiCollection()

    def execute(self, url: str) -> Dict[str, Any]:
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            info = loop.run_until_complete(
                self.generator.rex_bilibili(url)
            )

            return {"info": info}
        except Exception as e:
            return {"info": f"解析视频失败: {str(e)}"}

class BilibiliSearchBlock(Block):
    """B站视频搜索 Block"""
    name = "bilibili_search"
    description = "通过标题搜索B站视频"
    container: DependencyContainer
    inputs = {
        "keyword": Input(name="keyword", label="搜索关键词", data_type=str, description="视频标题关键词")
    }

    outputs = {
        "info": Output(name="info", label="视频信息", data_type=str, description="搜索到的视频信息")
    }

    def __init__(
        self,
        name: str = None,
    ):
        super().__init__(name)
        self.generator = ApiCollection()

    def execute(self, keyword: str) -> Dict[str, Any]:
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            sender = self.container.resolve(IMMessage).sender
            info = loop.run_until_complete(
                self.generator.search_bilibili_video_by_title(keyword,sender = sender.group_id if sender.chat_type == ChatType.GROUP else sender.user_id)
            )

            return {"info": info}
        except Exception as e:
            return {"info": f"搜索视频失败: {str(e)}"}
