from ..lark import *
from ..lark_robot import *


def test_send_text_message():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    send_text_message(
        token_info,
        "open_id",
        "ou_dd7d696370758f2018cd0358a25d8ddd",
        "hello\n test",
        "at_all",
        "",
        "",
    )


def test_send_text_message2():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    send_text_message(
        token_info,
        "chat_id",
        "oc_6988a11de7f725f37ac1d1664eaade20",
        "hello",
        "all",
        "ou_dd7d696370758f2018cd0358a25d8ddd",
        "Gbot",
    )


def test_send_file_message():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    send_file_message(
        token_info,
        "open_id",
        "ou_dd7d696370758f2018cd0358a25d8ddd",
        "image",
        r"C:\Users\Administrator\Pictures\Screenshots\_2b2513e5-7f7a-48a1-92de-1b4d6fa29a82.jpg",
    )
