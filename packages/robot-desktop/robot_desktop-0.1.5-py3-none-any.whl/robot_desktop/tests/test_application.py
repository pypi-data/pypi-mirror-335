import os
import time

import uiautomation
import xpath
from robot_base import log_util

from ..find_by_xpath import ControlNode
from ..index import open_app, window_activate
from ..application import find_controls_by_id


def setup_function():
    os.environ["project_path"] = (
        r"D:\Program Files\GoBot\data\ca990806-ec6b-4d6e-99d5-aab33f4969b1\gobot"
    )
    log_util.Logger("", "INFO")


def teardown():
    pass


def test_open_app():
    open_app(
        executable_path=r"D:\code\GoBot\gobot\build\bin\GoBot.exe",
        work_dir=r"D:\code\GoBot\gobot\build\bin",
        style="max",
        is_admin=True,
    )


def test_find_controls_by_id():
    controls = find_controls_by_id("67ba964633e041bdb52c176846fdf5d0")
    print(controls)


def test_window_activate():
    window_activate(
        windows_element={
            "name": "导航[工具栏]",
            "xpath": "/WindowControl[@name='微信']",
            "frameXpath": None,
        },
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "9jl99FTcDT_Pojvn",
            "code_line_number": "1",
            "code_file_name": "主流程",
            "code_block_name": "激活窗口",
        },
    )


def test_send_keys():
    time.sleep(2)
    uiautomation.SendKeys("中外")


def test_find_by_xpath():
    root = ControlNode(uiautomation.GetRootControl())

    result = xpath.find(
        "/PaneControl[@name='任务栏']/PaneControl[@name='DesktopWindowXamlSource']/PaneControl[1]/PaneControl[1]",
        root,
    )
    print(len(result))
