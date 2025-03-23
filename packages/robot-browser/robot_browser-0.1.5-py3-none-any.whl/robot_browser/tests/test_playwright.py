import os
import time

import robot_basic
from robot_base import log_util

from ..index import *


def setup_function():
    log_util.Logger("", "INFO")


def test_mkdir():
    user_data_dir = os.path.join(os.path.expanduser("~"), "GoBot", "browser", "chrome")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)


def test_wait_download_end():
    import robot_basic

    browser_instance = open_browser(
        browser_type="chrome",
        executable_path="C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
        url="https://sahitest.com/demo/saveAs.htm",
        timeout=3000,
        is_headless=False,
        is_stealth=False,
        privacy_mode=False,
        extra_args="--no-sandbox --disable-gpu",
        exception="error",
        local_data=locals(),
        code_map_id="jYn2PlICuWec8owU",
    )
    download_wrapper = start_download_listen(
        browser=browser_instance,
        exception="error",
        local_data=locals(),
        code_map_id="uhUlAW3cE2spy1YG",
    )
    element_click(
        element_type="locator",
        browser=browser_instance,
        frame_selector="",
        element_selector="//a[@href='/demo/testsaveas.zip']",
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        exception="error",
        local_data=locals(),
        code_map_id="gLFkegpuAFsU1gKB",
    )
    download_path = wait_download_end(
        browser=browser_instance,
        download_wrapper=download_wrapper,
        download_dir=r"D:\ProgramData\tmp",
        timeout=30,
        exception="error",
        local_data=locals(),
        code_map_id="Y27ZliLTaHsYYK2q",
    )
    robot_basic.print_log(
        log_level="info",
        expression=download_path,
        local_data=locals(),
        code_map_id="BCF8A0FrlMJ5ZAsm",
    )


def test_find_element():
    browser_instance = open_browser(
        browser_type="chrome",
        executable_path="C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
        url="https://sahitest.com/demo/iframesTest.htm",
        timeout=3000,
        is_headless=False,
        is_stealth=False,
        exception="error",
        local_data=locals(),
        code_map_id="jYn2PlICuWec8owU",
    )
    time.sleep(5)
    find_element(
        browser=browser_instance,
        frame_selector="//body/iframe | //body/iframe",
        element_selector="//a[@class='a x'][1]",
        highlight=True,
        exception="error",
        local_data=locals(),
        code_map_id="gLFkegpuAFsU1gKB",
    )
    time.sleep(5)


def test_switch_page():
    browser_instance = open_browser(
        browser_type="chrome",
        executable_path="C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
        url="https://www.toutiao.com/?wid=1721473241401",
        user_data_dir="D:\\ProgramData\\browser",
        download_path="D:\\ProgramData\\download",
        extension_path="D:\\Program Files\\GoBot\\chrome\\GoBotExtension",
        timeout=3000,
        is_headless=False,
        is_stealth=False,
        local_data=locals(),
        privacy_mode=False,
        code_block_extra_data={
            "exception": "error",
            "code_map_id": "RKEE6BdTJFvWDKlL",
            "code_block_name": "打开网页",
        },
    )
    element_click(
        element_type="locator",
        browser=browser_instance,
        frame_selector="",
        element_selector="//div[@class='publisher-icon']/a",
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        local_data=locals(),
        code_block_extra_data={
            "exception": "error",
            "code_map_id": "Cm7BHpyFGzToZcYe",
            "code_block_name": "点击元素",
        },
    )
    switch_page(
        match_strategy="equals",
        browser=browser_instance,
        url="https://mp.toutiao.com/profile_v4/graphic/publish",
        title="",
        bring_to_front=False,
        local_data=locals(),
        code_block_extra_data={
            "retry": True,
            "exception": "error",
            "retry_count": 6,
            "retry_interval": 2,
            "code_map_id": "GqSNgIzQuGmUtbcN",
            "code_block_name": "切换页面",
        },
    )
    element_fill(
        element_type="locator",
        browser=browser_instance,
        frame_selector="",
        element_selector="//textarea",
        element=None,
        content="免费云服务器，真香",
        clear=False,
        simulate=False,
        delay=3000,
        local_data=locals(),
        code_block_extra_data={
            "exception": "error",
            "code_map_id": "jVqWiPGNE0RXAAPp",
            "code_block_name": "元素中输入",
        },
    )
    element_fill(
        element_type="locator",
        browser=browser_instance,
        frame_selector="",
        element_selector="//div[@class='ProseMirror']",
        element=None,
        content="",
        clear=False,
        simulate=False,
        delay=3000,
        local_data=locals(),
        code_block_extra_data={
            "exception": "error",
            "code_map_id": "UDOXBiQw72__tqii",
            "code_block_name": "元素中输入",
        },
    )


def test_dialog_listen():
    log_util.Logger("", "DEBUG")
    browser_instance = open_browser(
        browser_type="chrome",
        executable_path="C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
        url="https://sahitest.com/demo/alertTest.htm",
        user_data_dir="D:\\ProgramData\\browser",
        download_path="D:\\ProgramData\\tmp",
        extension_path="D:\\Program Files\\GoBot\\chrome\\GoBotExtension",
        timeout=30000,
        is_headless=False,
        is_stealth=False,
        privacy_mode=False,
        local_data=locals(),
        code_block_extra_data={
            "exception": "error",
            "code_map_id": "JtJshAiPxJcEU0WF",
            "code_block_name": "打开网页",
        },
    )
    time.sleep(10)
    with browser_instance.page.expect_event("dialog") as dialog_info:
        print(dialog_info.value.message)
    dialog_info.value.accept()
    time.sleep(1)


def test_element_fill():
    browser_instance = open_browser(
        browser_type="chrome",
        executable_path="C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
        url="https://rpaservice.chinaums.com/rpa-console/login.html",
        user_data_dir="D:\\ProgramData\\browser",
        download_path="",
        extension_path="D:\\Program Files\\GoBot\\browser\\chrome-extension",
        timeout=3000,
        is_headless=False,
        is_stealth=False,
        privacy_mode=False,
        local_data=locals(),
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "qoIfl1swDHpCAw39",
            "code_block_name": "打开网页",
        },
    )
    element_fill(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "element_id": "25fd4a9021da4589a92de1cb833472fe",
            "xpath": "//DIV[@class='login-box-body box']/DIV[1]/INPUT[1]",
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        content="12324",
        clear=False,
        simulate=False,
        delay=3000,
        local_data=locals(),
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "S8teh0qTxhosNDY2",
            "code_block_name": "元素中输入",
        },
    )


def test_wait_element():
    browser_instance = open_browser(
        browser_type="chrome",
        executable_path="C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
        url="https://www.abeiyun.com/login/",
        user_data_dir="D:\\ProgramData\\browser",
        download_path="D:\\ProgramData\\tmp",
        extension_path="D:\\Program Files\\GoBot\\browser\\chrome-extension",
        timeout=30000,
        is_headless=False,
        is_stealth=False,
        privacy_mode=False,
        local_data=locals(),
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "FIptsfmO3OiJm4LJ",
            "code_block_name": "打开网页",
        },
    )
    element_exist = wait_element(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "element_id": "429ecefb3f2a4c889dd2e77e59dcd98f",
            "xpath": "//INPUT[@id='loginSubmit']",
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        display="display",
        timeout=3000,
        local_data=locals(),
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "APdbvweSzp_TDsHF",
            "code_block_name": "等待元素出现(消失)",
        },
    )


def test_switch_page_2():
    browser_instance = open_browser(
        browser_type="chrome",
        executable_path="C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
        url="https://www.abeiyun.com/login/",
        user_data_dir="D:\\ProgramData\\browser",
        download_path="",
        extension_path="",
        timeout=3000,
        is_headless=False,
        is_stealth=False,
        privacy_mode=False,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "tCropUicfPzdEe7b",
            "code_line_number": "1",
            "code_file_name": "主流程",
            "code_block_name": "打开网页",
        },
    )
    element_exist = wait_element(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "头像[SPAN]",
            "xpath": "//SPAN[@class='my-acct']",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        display="display",
        timeout=3000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "j9VITNt2P0A_t3s8",
            "code_line_number": "2",
            "code_file_name": "主流程",
            "code_block_name": "等待元素出现(消失)",
        },
    )
    if robot_basic.basic_condition(
        expression1=element_exist,
        relation="isTrue",
        expression2=None,
        code_block_extra_data={
            "code_map_id": "nJ4N0AjONBi5kJuy",
            "code_line_number": "3",
            "code_file_name": "主流程",
            "code_block_name": "If条件",
        },
    ):
        element_click(
            element_type="pick",
            browser=browser_instance,
            pick_element={
                "name": "控制台[A]",
                "xpath": "//UL[@class='header-tools-list']/LI[2]/A[text()='控制台']",
                "frameXpath": None,
            },
            frame_selector=None,
            element_selector=None,
            element=None,
            button="left",
            modifiers="",
            position="center-center",
            click_count=1,
            force=False,
            timeout=30000,
            code_block_extra_data={
                "exception": {
                    "exception": "error",
                    "retry": "False",
                    "retry_count": 1,
                    "retry_interval": 1,
                },
                "code_map_id": "o5zWdWe5MrJgnzDU",
                "code_line_number": "4",
                "code_file_name": "主流程",
                "code_block_name": "点击元素",
            },
        )
    else:
        element_fill(
            element_type="pick",
            browser=browser_instance,
            pick_element={
                "name": "手机号输入框",
                "xpath": "//INPUT[@id='userName']",
                "frameXpath": None,
            },
            frame_selector=None,
            element_selector=None,
            element=None,
            content="15527903378",
            clear=False,
            simulate=False,
            delay=3000,
            code_block_extra_data={
                "exception": {
                    "exception": "error",
                    "retry": "False",
                    "retry_count": 1,
                    "retry_interval": 1,
                },
                "code_map_id": "h7Q7gtnwA4MGVZSm",
                "code_line_number": "6",
                "code_file_name": "主流程",
                "code_block_name": "元素中输入",
            },
        )
        element_fill(
            element_type="pick",
            browser=browser_instance,
            pick_element={
                "name": "密码输入框",
                "xpath": "//INPUT[@id='passwordInput']",
                "frameXpath": None,
            },
            frame_selector=None,
            element_selector=None,
            element=None,
            content="mance19910715@",
            clear=False,
            simulate=False,
            delay=3000,
            code_block_extra_data={
                "exception": {
                    "exception": "error",
                    "retry": "False",
                    "retry_count": 1,
                    "retry_interval": 1,
                },
                "code_map_id": "tS1sW1e8TiEAxuPR",
                "code_line_number": "7",
                "code_file_name": "主流程",
                "code_block_name": "输入密码",
            },
        )
        element_click(
            element_type="pick",
            browser=browser_instance,
            pick_element={
                "name": "登录按钮",
                "xpath": "//INPUT[@id='loginSubmit']",
                "frameXpath": None,
            },
            frame_selector=None,
            element_selector=None,
            element=None,
            button="left",
            modifiers="",
            position="center-center",
            click_count=1,
            force=False,
            timeout=30000,
            code_block_extra_data={
                "exception": {
                    "exception": "error",
                    "retry": "False",
                    "retry_count": 1,
                    "retry_interval": 1,
                },
                "code_map_id": "FUnsWHO5BQM1NxJ2",
                "code_line_number": "8",
                "code_file_name": "主流程",
                "code_block_name": "点击元素",
            },
        )
    # EndIf
    element_click(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "产品[A]",
            "xpath": "//DIV[@class='menu-list']/UL[1]/LI[3]/A[1]",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "fVzB2lAF1IL4q-LX",
            "code_line_number": "10",
            "code_file_name": "主流程",
            "code_block_name": "点击元素",
        },
    )
    element_click(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "免费云服务器[DIV]",
            "xpath": "//DIV[@class='left navbar-collapse']/DL[1]/DD[1]/DIV[2]",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "OBG8Wy7UdHB-gfa_",
            "code_line_number": "11",
            "code_file_name": "主流程",
            "code_block_name": "点击元素",
        },
    )
    element_click(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "免费延期[BUTTON]",
            "xpath": "//DIV[@class='freevps-table']/DIV[6]/DIV[3]/DIV[1]/BUTTON[1]",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "61mCGpapBV1SmKXQ",
            "code_line_number": "12",
            "code_file_name": "主流程",
            "code_block_name": "点击元素",
        },
    )
    element_click(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "百度知道[A]",
            "xpath": "//DIV[@class='alert-info']/A[7]",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "sAUmojr0eUiTHty8",
            "code_line_number": "13",
            "code_file_name": "主流程",
            "code_block_name": "点击元素",
        },
    )
    robot_basic.delay(
        expression=10,
        code_block_extra_data={
            "code_map_id": "PBpCcNwfr3_dCls7",
            "code_line_number": "14",
            "code_file_name": "主流程",
            "code_block_name": "延时",
        },
    )
    switch_page(
        browser=browser_instance,
        match_target="url",
        match_strategy="contains",
        url="zhidao.baidu.com/search",
        title=None,
        bring_to_front=True,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "True",
                "retry_count": "5",
                "retry_interval": 1,
            },
            "code_map_id": "YRer1JQPo3lDaBN9",
            "code_line_number": "15",
            "code_file_name": "主流程",
            "code_block_name": "切换页面",
        },
    )
    element_fill(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "搜索框",
            "xpath": "//INPUT[@id='kw']",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        content="免费服务器",
        clear=True,
        simulate=False,
        delay=3000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "v8t9VrLYQz3jkLeW",
            "code_line_number": "16",
            "code_file_name": "主流程",
            "code_block_name": "元素中输入",
        },
    )
    element_click(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "百度一下[BUTTON]",
            "xpath": "//BUTTON[@id='search-btn']",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "02Md-W9X9j3uhQSs",
            "code_line_number": "17",
            "code_file_name": "主流程",
            "code_block_name": "点击元素",
        },
    )
    element_click(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "国外十大免费服务器(优质选择供您选择)[A]",
            "xpath": "//DIV[@id='wgt-list']/DL/DT/A[contains(@data-log, '免费服务器')][1]",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "thEbR60SBAdQ1hM5",
            "code_line_number": "18",
            "code_file_name": "主流程",
            "code_block_name": "点击元素",
        },
    )
    robot_basic.delay(
        expression=5,
        code_block_extra_data={
            "code_map_id": "9SN8MnMIHrhkmp-3",
            "code_line_number": "19",
            "code_file_name": "主流程",
            "code_block_name": "延时",
        },
    )
    switch_page(
        browser=browser_instance,
        match_target="url",
        match_strategy="contains",
        url="https://zhidao.baidu.com/question",
        title=None,
        bring_to_front=True,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "True",
                "retry_count": "5",
                "retry_interval": 1,
            },
            "code_map_id": "_GRfRoD8XCxl_gVS",
            "code_line_number": "20",
            "code_file_name": "主流程",
            "code_block_name": "切换页面",
        },
    )
    element_click(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "评论[SPAN]",
            "xpath": "//SPAN[@class='comment ']",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "zP8D0Ak3c7ZEDz1F",
            "code_line_number": "21",
            "code_file_name": "主流程",
            "code_block_name": "点击元素",
        },
    )
    element_click(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "TEXTAREA",
            "xpath": "//DIV[@class='mini-editor focus']/TEXTAREA[1]",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "k0ez8_72NzAp2JSg",
            "code_line_number": "22",
            "code_file_name": "主流程",
            "code_block_name": "点击元素",
        },
    )
    keyboard_input(
        browser=browser_instance,
        content="国内的云厂商阿贝云也提供免费的云服务，阿贝云 https://www.abeiyun.com",
        delay=0,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "31dO9ME9jZTj6AlW",
            "code_line_number": "23",
            "code_file_name": "主流程",
            "code_block_name": "键盘输入",
        },
    )
    element_click(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "发表[A]",
            "xpath": "//DIV[@class='comment-action-bar line']/DIV/A[@class='comment-submit']",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        button="left",
        modifiers="",
        position="center-center",
        click_count=1,
        force=False,
        timeout=30000,
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "62VB7Cf9_ADx01kH",
            "code_line_number": "24",
            "code_file_name": "主流程",
            "code_block_name": "点击元素",
        },
    )
    element_capture(
        element_type="pick",
        browser=browser_instance,
        pick_element={
            "name": "起航知识小百科2024-05-31 · 百度认证:淮安腾云起...[DIV]",
            "xpath": "//DIV[@class='wgt-best\n                ']",
            "frameXpath": None,
        },
        frame_selector=None,
        element_selector=None,
        element=None,
        save_path="D:\\ProgramData\\tmp\\test.png",
        code_block_extra_data={
            "exception": {
                "exception": "error",
                "retry": "False",
                "retry_count": 1,
                "retry_interval": 1,
            },
            "code_map_id": "BO-3NDFTNzXzoJzs",
            "code_line_number": "25",
            "code_file_name": "主流程",
            "code_block_name": "元素截图",
        },
    )
    页面URL = robot_basic.set_param(
        variable_type="any",
        variable_value=browser_instance.page.ulr,
        code_block_extra_data={
            "code_map_id": "Aqt8KMJEdCmOMBrq",
            "code_line_number": "26",
            "code_file_name": "主流程",
            "code_block_name": "设置变量",
        },
    )
    robot_basic.print_log(
        log_level="info",
        expression=页面URL,
        code_block_extra_data={
            "code_map_id": "Vh5Jx7Cx3K3M0hHK",
            "code_line_number": "27",
            "code_file_name": "主流程",
            "code_block_name": "打印日志",
        },
    )
