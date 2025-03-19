"""
内容分析页面数据采集
"""

from functools import partial
from random import uniform
from time import sleep
from typing import Callable

from DrissionPage import Chromium

from .._utils import Utils
from ._dict import Dictionary
from ._types import Video


class Urls:
    content_analysis = 'https://creator.douyin.com/creator-micro/data-center/content'


class DataPacketUrls:
    works__overview = (
        'https://creator.douyin.com/janus/douyin/creator/data/item_analysis/overview'
    )
    """投稿数据概览"""
    works__list = 'https://creator.douyin.com/web/api/creator/item/list'


class Content:
    def __init__(self, browser: Chromium):
        self._browser = browser
        self._timeout = 15
        self._interval_sleep_range = (3, 4.5)

    def get__works__list(
        self,
        timeout: float = None,
        interval_sleep_range: tuple = None,
        show_msg=True,
        as_dict=False,
    ):
        """
        获取作品/投稿列表

        Args:
            timeout: 超时时间，默认 15 秒
            interval_sleep_range: 间隔休眠时间范围，默认 (3, 4.5) 秒
            show_msg: 是否显示内部日志信息
            as_dict: 是否返回格式化后的字典列表, 默认 False 返回视频对象列表
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        page.listen.start(
            targets=DataPacketUrls.works__overview, method='POST', res_type='XHR'
        )
        page.get(Urls.content_analysis)
        if not page.listen.wait(timeout=_timeout):
            raise TimeoutError('进入内容分析页面获取投稿概览数据超时')

        target_btn = page.ele('t:span@@text()=投稿列表', timeout=3)
        if not target_btn:
            raise RuntimeError('未找到 [投稿列表] 按钮')

        def get_video_list(callback: Callable):
            """获取视频列表"""

            page.listen.start(
                targets=DataPacketUrls.works__list, method='GET', res_type='XHR'
            )
            callback()
            packet = page.listen.wait(timeout=_timeout)
            if not packet:
                raise TimeoutError('获取视频列表超时')

            resp: dict = packet.response.body
            if not isinstance(resp, dict):
                raise TypeError('视频列表数据包格式非预期的 dict 类型')

            if 'items' not in resp:
                raise KeyError('数据包中未找到 items 字段')

            items: list[dict] = resp['items']
            if not isinstance(items, list):
                raise TypeError('数据包中的 items 字段非预期的 list 类型')

            return [Video(**item) for item in items], resp.get('has_more')

        get_video_list(lambda: target_btn.click(by_js=True))

        # 修改日期范围为 全部
        date_input = page.ele('t:input@@placeholder=开始日期', timeout=3)
        if not date_input:
            raise RuntimeError('未找到日期输入框')
        date_input.click(by_js=True)
        all_date_btn = page.ele(
            't:div@@class^douyin-creator-pc-datepicker-quick-control@@text()=全部',
            timeout=3,
        )
        if not all_date_btn:
            raise RuntimeError('未找到日期选择器中的 [全部] 按钮')

        sleep(2.5)
        video_list, has_more = get_video_list(lambda: all_date_btn.click(by_js=True))

        _interval_sleep_range = (
            interval_sleep_range
            if isinstance(interval_sleep_range, (list, tuple))
            else self._interval_sleep_range
        )

        sleep(1.5)
        page.scroll.to_bottom()
        while has_more:
            if show_msg is True:
                print('- 滚动表格加载更多视频列表')

            container = page.ele('c:div.douyin-creator-pc-table-body', timeout=3)
            if not container:
                raise RuntimeError('未找到视频列表容器元素')

            try:
                _video_list, has_more = get_video_list(
                    partial(container.scroll.to_bottom)
                )
                video_list.extend(_video_list)
                if not has_more:
                    break
            except Exception as e:
                if show_msg is True:
                    print(f'加载更多视频列表失败: {e}')
                break

            sleep(uniform(*_interval_sleep_range))

        page.close()

        if as_dict is True:
            return [
                Utils.dict_mapping(item.as_dict(), Dictionary.works.video__detail)
                for item in video_list
            ]

        return video_list
