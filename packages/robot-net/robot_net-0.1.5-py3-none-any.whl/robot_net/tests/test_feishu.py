import sys

from robot_base import log_util

from ..lark import *
from ..lark_sheets import *
from ..lark_sheets_data import *
from ..lark_bitable import *


def setup_function():
    log_util.Logger("", "DEBUG")


def test_get_app_access_token():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    print(token_info)


def test_add_sheet():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    add_sheet(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/sheets/TcsXsvR5nhu0Alt3hlacPF9Knxd",
        "test_sheet1",
        5,
    )


def test_get_sheets():
    token_info = get_app_access_token(
        "cli_a7b774556f3d500e", "xi7v9WwIQtBNKLurLQix5gGSif4UEnWo"
    )
    result = get_sheets(
        token_info, "https://icnnzf7ej5lr.feishu.cn/sheets/R4H6swdeAhp6DatElXkc2K0znvf"
    )
    print(result)


def test_copy_sheet():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    copy_sheet(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/sheets/TcsXsvR5nhu0Alt3hlacPF9Knxd",
        "test_sheet1",
        "test_sheet5",
    )


def test_delete_sheet():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    delete_sheet(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/sheets/TcsXsvR5nhu0Alt3hlacPF9Knxd",
        "Sheet1",
    )


def test_update_sheet():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    update_sheet(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/sheets/TcsXsvR5nhu0Alt3hlacPF9Knxd",
        "Sheet2",
        "Sheet1",
        True,
    )


def test_get_sheet():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    result = get_sheet(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/sheets/TcsXsvR5nhu0Alt3hlacPF9Knxd",
        "测试",
    )
    print(result)


def test_write_sheet_data():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    write_sheet_data(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/sheets/DAiKsRrxqhJUy2tTByHcRPSnnYV",
        "Sheet1",
        "cell",
        "A1",
        1,
        1,
        "1",
    )


def test_get_sheet_data():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    result = get_sheet_data(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/sheets/TcsXsvR5nhu0Alt3hlacPF9Knxd",
        "Sheet1",
        "range",
        "A1",
        1,
        1,
        2,
        1,
        "ToString",
        "FormattedString",
    )
    print(result)


def test_insert_sheet_data():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    insert_sheet_data(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/sheets/TcsXsvR5nhu0Alt3hlacPF9Knxd?sheet=37prOM",
        "测试",
        "range",
        "A1",
        1,
        1,
        [["测试1", "测试2"], ["测试11", "测试22"], ["测试111", "测试222"]],
    )


def test_sheet_append_row():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    append_sheet_data(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/sheets/TcsXsvR5nhu0Alt3hlacPF9Knxd",
        "测试",
        "col",
        ["", "4"],
        start_column="C",
        start_row=10,
    )


def test_get_bit_sheet_data():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    data = get_bit_sheet_data(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/base/QJHIbuLVOaRktusG2iLcxdsFnpc?table=tblTHLJ8WgnXCKQu&view=vew17zsyjh",
    )
    print(data)


def test_delete_bit_sheet_record():
    token_info = get_app_access_token(
        "cli_a7a1cc119df9500e", "e4oGwGbZInBfyWk9OQ9khgD2XxBfYJdn"
    )
    delete_bit_sheet_record(
        token_info,
        "https://icnnzf7ej5lr.feishu.cn/base/Dlk1bVngYafX53s5UQ9cS8Lvnyb?table=tblEzDVKtKmOBh5P&view=vewjuB1bx3",
        "recuFqNRt0I8MR",
    )
