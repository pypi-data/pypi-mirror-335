# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-30 13:12
# @Author : 毛鹏
import platform
import subprocess
from typing import Optional

import uiautomation as auto
from uiautomation.uiautomation import WindowControl


class NewWindows:

    def __init__(self, win_path: str, win_title: str):
        self.win_path = win_path
        self.win_title = win_title
        self.windows: Optional[None | WindowControl] = None

    def new_windows(self):
        subprocess.Popen(self.win_path)
        self.windows = auto.WindowControl(ClassName='ApplicationFrameWindow', Name=self.win_title)
        return self.windows
