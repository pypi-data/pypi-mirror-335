"""
作品管理页面数据采集
"""

from random import uniform
from time import sleep
from typing import Callable, Literal

from DrissionPage import Chromium
from DrissionPage._pages.mix_tab import MixTab

from .._utils import Utils
from ._dict import Dictionary
from ._types import Video


class Urls:
    works = 'https://creator.douyin.com/creator-micro/content/manage'


class DataPacketUrls:
    works__list = 'https://creator.douyin.com/janus/douyin/creator/pc/work_list'


class Works:
    def __init__(self, browser: Chromium):
        self._browser = browser
        self._timeout = 15
        self._interval_sleep_range = (3, 4.5)

    def __works_enter_check(self, page: MixTab, timeout: float):
        """作品管理页面进入检测"""

        page.listen.start(
            targets=DataPacketUrls.works__list, method='GET', res_type=['Fetch', 'XHR']
        )
        page.get(Urls.works)
        packet = page.listen.wait(timeout=timeout)
        if not packet:
            raise TimeoutError('进入作品管理页面后获取数据超时')

        resp = packet.response.body
        if not isinstance(resp, dict):
            raise TypeError('返回的数据包非预期 dict 类型')
        if 'items' not in resp:
            raise KeyError('数据包中未找到 items 字段')
        items: list[dict] = resp['items']
        if not isinstance(items, list):
            raise TypeError('数据包中 items 字段非预期 list 类型')

        return packet, items, resp.get('max_cursor')

    def __return_video_dict_list(self, video_list: list[Video]):
        """以格式化后的字典列表返回视频对象列表"""

        return [
            Utils.dict_mapping(item.as_dict(), Dictionary.works.video__detail)
            for item in video_list
        ]

    def get__works__list(
        self,
        works_type: Literal['0', '1', '2'],
        timeout: float = None,
        interval_sleep_range: tuple = None,
        show_msg=True,
        as_dict=False,
    ):
        """
        获取作品列表

        Args:
            works_type: 作品类型, 0: 全部, 1: 已发布, 2: 私密
            timeout: 等待数据包超时时间, 默认 15 秒
            interval_sleep_range: 间隔休眠时间范围, 默认 (3, 4.5) 秒
            show_msg: 是否显示提示信息, 默认 True
            as_dict: 是否返回格式化后的字典列表, 默认 False 返回视频对象列表
        Returns:
            作品对象列表
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        packet, items, first_next_cursor = self.__works_enter_check(page, _timeout)

        if not items:
            page.close()
            return

        video_list: list[Video] = []
        next_cursor = 0
        if packet.request.params.get('status') == works_type:
            video_list = [Video(**item) for item in items]
            next_cursor = first_next_cursor
            if not next_cursor:
                page.close()
                if as_dict is True:
                    return self.__return_video_dict_list(video_list)

                return video_list

        packet_headers = {
            k.lower(): v
            for k, v in packet.request.headers.items()
            if k.lower() in ['referer', 'user-agent', 'x-secsdk-csrf-token']
        }
        packet_query = {
            k: v
            for k, v in packet.request.params.items()
            if k in ['aid', 'count', 'scene', 'device_platform']
        }

        user_agent: str = packet_headers['user-agent']
        browser_name = user_agent[: user_agent.index('/')]
        browser_version = user_agent[user_agent.index('/') + 1 :]

        pub_headers = {**packet_headers}
        pub_query = {
            **packet_query,
            'status': works_type,
            'cookie_enabled': 'true',
            'screen_width': '1920',
            'screen_height': '1080',
            'browser_language': 'en-US',
            'browser_platform': 'Win32',
            'browser_name': browser_name,
            'browser_version': browser_version,
            'browser_online': 'true',
            'timezone_name': 'Asia/Shanghai',
        }

        def query_api(next_cursor: int = 0):
            query_data = {**pub_query, 'max_cursor': next_cursor}
            if not page.get(
                DataPacketUrls.works__list,
                params=query_data,
                headers=pub_headers,
                timeout=_timeout,
            ):
                if show_msg is True:
                    print('- 通过 API 获取作品列表失败')
                return

            try:
                resp: dict = page.response.json()
            except Exception as e:
                if show_msg is True:
                    print(f'- API 返回的数据包解析失败: {e}')
                return

            if 'items' not in resp:
                if show_msg is True:
                    print('- API 返回的数据包中未找到 items 字段')
                return

            items: list[dict] = resp['items']
            if not isinstance(items, list):
                if show_msg is True:
                    print('- API 返回的数据包中 items 字段非预期 list 类型')
                return

            max_cursor: int = resp.get('max_cursor')
            return [Video(**item) for item in items], max_cursor

        curr_page = 1 if not video_list else 2
        _interval_sleep_range = (
            interval_sleep_range
            if isinstance(interval_sleep_range, tuple)
            else self._interval_sleep_range
        )

        page.change_mode('s', go=False)
        for _ in range(500):
            if show_msg is True:
                print(f'- 通过 API 获取第 {curr_page} 页视频列表')

            result = query_api(next_cursor)
            if not result:
                break

            video_list.extend(result[0])
            _next_cursor = result[1]
            if not _next_cursor or _next_cursor == next_cursor or len(video_list) == 0:
                break

            curr_page += 1
            next_cursor = _next_cursor
            sleep(uniform(*_interval_sleep_range))

        page.change_mode('d', go=False)
        page.close()

        if as_dict is True:
            return self.__return_video_dict_list(video_list)

        return video_list

    def get__works__list__normal(
        self,
        works_type: str,
        timeout: float = None,
        interval_sleep_range: tuple = None,
        show_msg=True,
        as_dict=False,
    ):
        """
        获取作品列表 (通过页面访问)

        Args:
            works_type: 作品类型, 例如 全部作品/已发布, 具体可以查看页面
            timeout: 等待数据包超时时间, 默认 15 秒
            interval_sleep_range: 间隔休眠时间范围, 默认 (3, 4.5) 秒
            show_msg: 是否显示提示信息, 默认 True
            as_dict: 是否返回格式化后的字典列表, 默认 False 返回视频对象列表
        Returns:
            作品对象列表
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        _, items, first_next_cursor = self.__works_enter_check(page, _timeout)

        if not items:
            page.close()
            return

        def get_current_active_tab():
            """获取当前激活的类型选项卡"""
            curr_active_tab = page.ele(
                't:div@@class^tab-item@@class:active-', timeout=3
            )
            if not curr_active_tab:
                raise RuntimeError('未找到当前激活的选项卡')

            return curr_active_tab.text.strip()

        def get_video_list(callback: Callable):
            """获取视频列表数据包"""
            page.listen.start(
                targets=DataPacketUrls.works__list, method='GET', res_type='XHR'
            )
            callback()
            packet = page.listen.wait(timeout=_timeout)
            if not packet:
                raise TimeoutError('获取视频列表数据包超时')

            resp = packet.response.body
            if not isinstance(resp, dict):
                raise TypeError('返回的数据包非预期 dict 类型')
            if 'items' not in resp:
                raise KeyError('数据包中未找到 items 字段')
            items: list[dict] = resp['items']
            if not isinstance(items, list):
                raise TypeError('数据包中 items 字段非预期 list 类型')

            return [Video(**item) for item in items], resp.get('max_cursor')

        video_list: list[Video] = []
        next_cursor = 0
        if get_current_active_tab() != works_type:
            target_tab = page.ele(
                f't:div@@class^tab-item@@text()={works_type}', timeout=3
            )
            if not target_tab:
                raise RuntimeError(f'未找到 [{works_type}] 选项卡')

            video_list, next_cursor = get_video_list(
                lambda: target_tab.click(by_js=True)
            )
        else:
            video_list = [Video(**item) for item in items]
            next_cursor = first_next_cursor

        if not next_cursor:
            page.close()
            if as_dict is True:
                return self.__return_video_dict_list(video_list)

            return video_list

        _interval_sleep_range = (
            interval_sleep_range
            if isinstance(interval_sleep_range, tuple)
            else self._interval_sleep_range
        )

        for _ in range(500):
            if show_msg is True:
                print('- 滚动页面加载视频列表')

            try:
                _video_list, next_cursor = get_video_list(
                    lambda: page.scroll.to_bottom()
                )
                video_list.extend(_video_list)
                if not next_cursor:
                    break
            except Exception as e:
                if show_msg is True:
                    print(f'- 滚动页面加载视频列表出错: {e}')
                break

            sleep(uniform(*_interval_sleep_range))

        page.close()

        if as_dict is True:
            return self.__return_video_dict_list(video_list)

        return video_list
