"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-02-23
Author: Martian Bugs
Description: 数据中心模块数据采集
"""

from DrissionPage import Chromium

from .content import Content


class Data:
    def __init__(self, browser: Chromium):
        self._browser = browser

        self._content = None

    @property
    def content(self):
        if self._content is None:
            self._content = Content(self._browser)

        return self._content
