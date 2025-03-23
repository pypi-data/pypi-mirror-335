# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-04 10:43
# @Author : 毛鹏
import platform
from typing import Optional

from uiautomation import WindowControl

from mangokit import MysqlConnect, MysqlConingModel
from playwright.async_api import Page, BrowserContext
from uiautomator2 import Device

from mangokit.enums.tools_enum import StatusEnum
from mangokit.models.ui_model import EnvironmentConfigModel, EquipmentModel


class BaseData:

    def __init__(self, parent, project_product_id, test_data):
        super().__init__()
        self.parent = parent
        self.project_product_id = project_product_id
        self.test_data = test_data

        self.test_suite_id: Optional[int | None] = None
        self.case_id: Optional[int | None] = None
        self.case_step_details_id: Optional[int | None] = None

        self.page_step_id: Optional[int | None] = None
        self.is_step: bool = False

        self.equipment_config: Optional[EquipmentModel | None] = None

        self.environment_config: Optional[EnvironmentConfigModel | None] = None

        self.mysql_config: Optional[MysqlConingModel | None] = None  # mysql连接配置
        self.mysql_connect: Optional[MysqlConnect | None] = None  # mysql连接对象

        self.url: Optional[str | None] = None
        self.is_open_url = False
        self.switch_step_open_url = False
        self.package_name: Optional[str | None] = None

        self.page: Optional[Page | None] = None
        self.context: Optional[BrowserContext | None] = None
        self.android: Optional[Device | None] = None
        self.windows: Optional[None | WindowControl] = None

        self.download_path: Optional[str | None] = None
        self.screenshot_path: Optional[str | None] = None
        self.video_path: Optional[str | None] = None
        self.log = None

    def set_log(self, log):
        self.log = log
        return self

    def set_file_path(self, download_path, screenshot_path, video_path):
        self.download_path = download_path
        self.screenshot_path = screenshot_path
        self.video_path = video_path
        return self

    def set_case_id(self, case_id: int):
        self.case_id = case_id
        return self

    def set_case_step_details_id(self, case_step_details_id: int):
        self.case_step_details_id = case_step_details_id
        return self

    def set_test_suite_id(self, test_suite_id: int):
        self.test_suite_id = test_suite_id
        return self

    def set_step_open_url(self, switch_step_open_url: bool):
        self.switch_step_open_url = switch_step_open_url
        return self

    def set_page_step_id(self, page_step_id: int):
        self.page_step_id = page_step_id
        return self

    def set_environment_config(self, environment_config: EnvironmentConfigModel):
        self.environment_config = environment_config
        return self

    def set_equipment_config(self, equipment_config: EquipmentModel):
        self.equipment_config = equipment_config
        return self

    def set_is_step(self, is_step: bool):
        self.is_step = is_step
        return self

    def set_project_product_id(self, project_product_id: bool):
        self.project_product_id = project_product_id
        return self

    def set_url(self, url: str):
        self.url = url
        return self

    def set_page_context(self, page: Page, context: BrowserContext):
        self.page = page
        self.context = context

        return self

    def set_package_name(self, package_name: str):
        self.package_name = package_name
        return self

    def set_android(self, android: Device):
        self.android = android
        return self

    async def setup(self, test_data) -> None:
        self.url = None
        self.page = None
        self.context = None

        self.package_name = None
        self.android = None
        self.mysql_connect = None
        self.mysql_config = None
        self.test_data = test_data

    async def base_close(self, test_data):
        if self.context and isinstance(self.context, BrowserContext):
            await self.context.close()
        if self.page and isinstance(self.page, Page):
            await self.page.close()
        if self.mysql_connect:
            self.mysql_connect.close()
        await self.setup(test_data)

    def set_mysql(self, run_config: EnvironmentConfigModel):
        self.mysql_config = run_config.mysql_config
        if StatusEnum.SUCCESS.value in [run_config.db_c_status, run_config.db_rud_status]:
            self.mysql_connect = MysqlConnect(run_config.mysql_config,
                                              bool(run_config.db_c_status),
                                              bool(run_config.db_rud_status))
        return self
