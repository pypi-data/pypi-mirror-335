# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-04-24 10:43
# @Author : 毛鹏

from .android.new_android import NewAndroid
from .pc.new_windows import NewWindows
from .web.new_browser import NewBrowser
from typing import Optional


class DriverObject:

    def __init__(self):
        self.web: Optional[NewBrowser] = None
        self.android: Optional[NewAndroid] = None
        self.windows: Optional[NewWindows] = None

    def set_web(self, web_type: int, web_path: str, web_max=False, web_headers=False, web_recording=False,
                web_h5=None, is_header_intercept=False, ws=None):
        self.web = NewBrowser(web_type, web_path, web_max, web_headers, web_recording, web_h5, is_header_intercept, ws)

    def set_android(self, and_equipment: str):
        self.android = NewAndroid(and_equipment)

    def set_windows(self, win_path: str, win_title: str):
        self.windows = NewWindows(win_path, win_title)
