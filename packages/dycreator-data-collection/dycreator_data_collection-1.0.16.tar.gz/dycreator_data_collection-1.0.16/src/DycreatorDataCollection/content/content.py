"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-02-22
Author: Martian Bugs
Description: 内容管理模块数据采集
"""

from DrissionPage import Chromium

from .works import Works


class Content:
    def __init__(self, browser: Chromium):
        self._browser = browser

        self._works = None

    @property
    def works(self):
        """作品管理页面数据采集"""

        if self._works is None:
            self._works = Works(self._browser)

        return self._works
