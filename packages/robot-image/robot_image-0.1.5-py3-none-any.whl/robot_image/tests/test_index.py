import os
import time

import pyautogui

from ..index import (
    screen_size,
    get_dpi,
    find_target_position,
    find_target_position_by_template,
    find_target_position_by_sift,
    click_target,
    wait_target,
)


def setup_function():
    os.environ["project_path"] = (
        r"D:\ProgramData\data\project\8daa487d-e7e2-4aa1-bac1-5e1091a15681\gobot"
    )


def teardown():
    pass


def test_screen_size():
    print(screen_size())


def test_get_dpi():
    print(get_dpi() / 1.5)


def test_find_target_position():
    print(find_target_position("3gU-xTBd3gGrZHvv"))


def test_find_target_position_by_template():
    pyautogui.hotkey("win", "d")
    time.sleep(2)
    print(
        find_target_position_by_template(
            r"C:\Users\Administrator\Downloads\test.png", False, 0.9
        )
    )


def test_find_target_position_by_sift():
    pyautogui.hotkey("win", "d")
    time.sleep(2)
    print(
        find_target_position_by_sift(
            r"D:\ProgramData\data\project\8daa487d-e7e2-4aa1-bac1-5e1091a15681\gobot\.dev\snapshot\wFnwVTV24MzCNLep.png",
            0.9,
        )
    )


def test_click_target():
    pyautogui.hotkey("win", "d")
    time.sleep(2)
    click_target(
        r"C:\Users\Administrator\Downloads\test.png",
        True,
        0.9,
        show_mouse_position=True,
        button="right",
    )


def test_wait_target():
    # pyautogui.hotkey("win", "d")
    time.sleep(2)
    print(
        wait_target(
            r"C:\Users\Administrator\Downloads\test.png",
            True,
            0.9,
            wait_result="display",
            timeout=5,
        )
    )
