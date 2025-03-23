# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-03-05 20:39
# @Author : 毛鹏
import os

import sys


class ProjectDir:

    def __init__(self):
        self.folder_list = []
        self._root_path = self.init_project_path()
        self.init_folder()

    @staticmethod
    def init_project_path():
        current_directory = os.path.abspath(__file__)
        project_root_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_directory)))
        current_dir2 = os.path.dirname(sys.executable)
        if 'python.exe' not in sys.executable:
            project_root_directory = current_dir2
        return project_root_directory

    def init_folder(self):
        for i in self.folder_list:
            cache_dir = os.path.join(self._root_path, i)
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)

    def root_path(self):
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        else:
            return self._root_path

    def logs(self, folder_name='logs'):
        return os.path.join(self.root_path(), folder_name)

    def cache(self, folder_name='cache'):
        return os.path.join(self.root_path(), folder_name)


project_dir = ProjectDir()
