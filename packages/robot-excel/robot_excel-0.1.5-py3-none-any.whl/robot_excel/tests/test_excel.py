import json
import os
import typing

import robot_base
import robot_basic
import robot_excel

from .. import XlwingsExcel
from ..__init__ import (
    open_excel,
    close_excel,
    save_workbook,
    encrypt_workbook,
    get_opened_workbook,
    get_sheet_names,
    activate_sheet,
    insert_sheet,
    rename_sheet,
    copy_sheet,
    delete_sheet,
    move_sheet,
    get_used_range,
    get_row_count,
    get_column_count,
    get_content,
    write_cell,
)

excel: typing.Optional[XlwingsExcel] = None


def setup_function():
    # os.environ["project_path"] = (
    #     r"D:\Program Files\GoBot\data\ca990806-ec6b-4d6e-99d5-aab33f4969b1\gobot"
    # )
    robot_base.Logger(log_path="", level="DEBUG")
    # global excel
    # excel = open_excel(
    #     file_path=r"C:\Users\Administrator\Downloads\api2Y0GoB.xlsx",
    #     open_type="xlwings",
    #     is_visible=True,
    # )
    pass


def teardown_function():
    if excel:
        excel.close_app()


def test_open_excel():
    global excel
    excel = open_excel(
        file_path=r"C:\Users\Administrator\Downloads\祝福模板.xlsx",
        open_type="xlwings",
        is_visible=True,
    )
    close_excel(excel_app=excel, is_save=False, close_all=True)


def test_close_excel():
    global excel
    if excel:
        close_excel(excel_app=excel, is_save=False, close_all=True)
    excel = None


def test_encrypt_workbook():
    global excel
    if excel:
        encrypt_workbook(excel_app=excel, password="123456")


def test_get_opened_workbook():
    global excel
    excel = get_opened_workbook(r"api2Y0GoB.xlsx")


def test_get_sheet_names():
    print(get_sheet_names(excel_app=excel))


def test_activate_sheet():
    excel_instance = robot_excel.open_excel(
        file_path="C:\\Users\\Administrator\\Downloads\\api2Y0GoB.xlsx",
        open_type="xlwings",
        is_visible=True,
        password="",
        write_res_password="",
        local_data=locals(),
        code_block_extra_data={
            "code_map_id": "iUuYn6VuhffvT6ZY",
            "code_block_name": "打开Excel",
        },
    )
    sheet_names = robot_excel.get_sheet_names(
        excel_app=excel_instance,
        local_data=locals(),
        code_block_extra_data={
            "code_map_id": "DquOJo08p5pAXOXR",
            "code_block_name": "获取Sheet名称列表",
        },
    )
    robot_excel.activate_sheet(
        excel_app=excel_instance,
        active_type="index",
        sheet_name="",
        sheet_index=0,
        local_data=locals(),
        code_block_extra_data={
            "code_map_id": "ypKXpIDzjzf50Rqq",
            "code_block_name": "激活Sheet",
        },
    )
    robot_basic.print_log(
        log_level="info",
        expression=sheet_names,
        local_data=locals(),
        code_block_extra_data={
            "code_map_id": "gfoUnDWboFZSaPSS",
            "code_block_name": "打印日志",
        },
    )


def test_insert_sheet():
    insert_sheet(
        excel_app=excel, new_sheet_name="Sheet6", sheet_name="", is_before=False
    )
    save_workbook(excel_app=excel)


def test_rename_sheet():
    rename_sheet(excel_app=excel, sheet_name="Sheet6", new_sheet_name="Sheet8")
    save_workbook(excel_app=excel)


def test_copy_sheet():
    copy_sheet(excel_app=excel, sheet_name="Sheet8", new_sheet_name="Sheet9")
    save_workbook(excel_app=excel)


def test_delete_sheet():
    delete_sheet(excel_app=excel, sheet_name="Sheet2")
    save_workbook(excel_app=excel)


def test_move_sheet():
    move_sheet(
        excel_app=excel,
        target_type="index",
        sheet_name="Sheet5",
        target_sheet_name="Sheet3",
        is_before=False,
        index=300,
    )
    save_workbook(excel_app=excel)


def test_get_used_range():
    address = get_used_range(excel_app=excel, sheet_name="Sheet4")
    print(address)


def test_get_row_count():
    rows = get_row_count(
        excel_app=excel, sheet_name="Sheet4", by_type="column", column="G"
    )
    print(rows)


def test_get_column_count():
    rows = get_column_count(excel_app=excel, sheet_name="Sheet4", by_type="row", row=11)
    print(rows)


def test_get_content():
    content = get_content(
        excel_app=excel, sheet_name="Sheet4", range_type="column", column=8
    )
    print(content)


def test_write_cell():
    write_cell(
        excel_app=excel,
        sheet_name="Sheet4",
        cell_column="A",
        cell_row=1,
        value="111111",
    )
    save_workbook(excel_app=excel)


def test_read_content():
    excel_instance = open_excel(
        file_path="C:\\Users\\Administrator\\Downloads\\祝福模板.xlsx",
        open_type="xlwings",
        is_visible=False,
        create_new=True,
        password="",
        write_res_password="",
        code_block_extra_data={
            "code_map_id": "NJikyoFx2R9ETN5u",
            "code_line_number": "1",
            "code_file_name": "主流程",
            "code_block_name": "打开Excel",
        },
    )
    excel_data = get_content(
        excel_app=excel_instance,
        sheet_name="Sheet1",
        range_type="range",
        cell_column=None,
        cell_row=None,
        row=None,
        column=None,
        start_col="A",
        start_row="1",
        end_col="B",
        end_row="2",
        code_block_extra_data={
            "code_map_id": "u-OAxqcuu6acJm5I",
            "code_line_number": "2",
            "code_file_name": "主流程",
            "code_block_name": "读取Excel内容",
        },
    )
    robot_basic.print_log(
        log_level="info",
        expression=excel_data,
        code_block_extra_data={
            "code_map_id": "pVtdkxjTGuhj3PYs",
            "code_line_number": "3",
            "code_file_name": "主流程",
            "code_block_name": "打印日志",
        },
    )


def test_ocr_to_table():
    with open(
        r"C:\Users\Administrator\Downloads\orc_result.json", "r", encoding="utf-8"
    ) as f:
        content = f.read()
        data = json.loads(content)
        results = []
        for item in data:
            try:
                y = item["pos"].get("y", 0)
                if len(results) == 0:
                    results.append([item])
                    continue
            except:
                print(item)
            matched = False
            for result in results:
                if y + 10 > result[0]["pos"]["y"] > y - 10:
                    result.append(item)
                    matched = True
                    break
            if not matched:
                results.append([item])
        sorted(results, key=lambda x: x[0]["pos"]["y"])
        for result in results:
            sorted(result, key=lambda x: x["pos"]["x"])
        print(results)
