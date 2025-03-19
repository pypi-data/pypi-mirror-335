import aiohttp
import random
import json
import time
import asyncio
from typing import Dict, Any, Optional, Tuple, List
from kirara_ai.logger import get_logger
# ... existing code ...
from .bilibili import rex_bilibili, search_bilibili_video_by_title


logger = get_logger("ApiCollection")

class ApiCollection:

    def __init__(self):
        pass

    async def get_random_girl_video(self) -> str:
        """获取随机美女视频链接"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.lolimi.cn/API/xjj/xjj.php",
                    allow_redirects=False  # 不自动跟随重定向
                ) as response:
                    if response.status == 302:  # 检查是否有重定向
                        redirect_url = response.headers.get('Location')
                        if redirect_url:
                            return redirect_url
                        else:
                            raise Exception("未获取到重定向链接")
                    else:
                        raise Exception(f"请求失败，状态码: {response.status}")

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"获取视频链接失败: {str(e)}")

    async def weacherSearch(self, city: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.easyapi.com/weather/city.json?cityName={city}"
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    msg = result["message"]

                    if isinstance(msg, str):
                        import json
                        weather_data = json.loads(msg)
                        weather_info = []

                        # Add current weather
                        realtime = weather_data.get('realtime', {})
                        if realtime:
                            current = (
                                f"当前天气：{realtime['city_name']} {realtime['date']} {realtime['time']}\n"
                                f"温度：{realtime['weather']['temperature']}°C\n"
                                f"天气：{realtime['weather']['info']}\n"
                                f"湿度：{realtime['weather']['humidity']}%\n"
                                f"风况：{realtime['wind']['direct']} {realtime['wind']['power']}\n"
                            )
                            weather_info.append(current)

                        # Add forecast
                        weather_info.append("\n未来天气预报：")
                        for day in weather_data.get('weather', [])[:7]:  # Only show 7 days
                            date = day['date']
                            info = day['info']
                            air_info = day.get('airInfo', {})

                            forecast = (
                                f"\n{date} (周{day['week']}) {day['nongli']}\n"
                                f"白天：{info['day'][1]}，{info['day'][2]}°C，{info['day'][3]} {info['day'][4]}\n"
                                f"夜间：{info['night'][1]}，{info['night'][2]}°C，{info['night'][3]} {info['night'][4]}\n"
                            )

                            # Add air quality info if available
                            if air_info:
                                forecast += (
                                    f"空气质量：{air_info.get('quality', '无数据')} "
                                    f"(AQI: {air_info.get('aqi', '无数据')})\n"
                                    f"建议：{air_info.get('des', '无建议')}\n"
                                )

                            weather_info.append(forecast)
                        logger.info("".join(weather_info))
                        return "".join(weather_info)

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            return {
                "success": False,
                "message": f"网络请求失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "message": f"查询出错: {str(e)}"
            }

    async def get_random_cosplay(self, count: int = 5) -> List[str]:
        """获取随机cosplay图片链接列表"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.lolimi.cn/API/cosplay/api.php"
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    if result["code"] == "1" and "data" in result:
                        image_list = result["data"]["data"]
                        # 确保count不超过可用图片数量
                        count = min(count, len(image_list))
                        # 随机选择指定数量的图片
                        selected_images = random.sample(image_list, count)
                        return {"Title":result["data"]["Title"],"data":selected_images}
                    else:
                        raise Exception("API返回数据格式错误")

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"获取cosplay图片失败: {str(e)}")

    async def get_random_emoji(self) -> str:
        """获取随机表情包图片链接"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.lolimi.cn/API/dou/api.php"
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    if "data" in result and "image" in result["data"]:
                        return result["data"]["image"]
                    else:
                        raise Exception("API返回数据格式错误")

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"获取表情包失败: {str(e)}")

    async def get_sougou_image(self, keyword: str) -> str:
        """获取搜狗搜图结果"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.lolimi.cn/API/sgst/api.php?msg={keyword}&type=json"
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    if "data" in result and "url" in result["data"]:
                        return result["data"]["url"]
                    else:
                        raise Exception("API返回数据格式错误")

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"搜狗搜图失败: {str(e)}")

    async def rex_bilibili(self, url: str) -> str:
        return await rex_bilibili(url)

    async def search_bilibili_video_by_title(self, keyword: str,sender: str) -> str:
        return await search_bilibili_video_by_title(keyword,sender)

