import os
from io import BytesIO
from tempfile import SpooledTemporaryFile, NamedTemporaryFile
from typing import List, Dict, Any
from urllib.parse import quote

import numpy as np
from fastapi.responses import StreamingResponse
import pandas as pd
from styleframe import StyleFrame


def export_excel(header: List[str], data: List, file_name='download.xlsx') -> StreamingResponse:
    output = BytesIO()
    df = pd.DataFrame(data, columns=header)
    if df.empty:
        columns_and_rows_to_freeze = 'A1'
    else:
        columns_and_rows_to_freeze = 'A2'
    sf = StyleFrame(df)
    headers = {
        "Content-Disposition": f'attachment; filename="{quote(file_name)}"',
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    with StyleFrame.ExcelWriter(output) as excel_writer:
        sf.to_excel(excel_writer=excel_writer, columns_and_rows_to_freeze=columns_and_rows_to_freeze)
    output.seek(0)
    return StreamingResponse(output, media_type='xls/xlsx', headers=headers)


def export_csv(data: List, file_name='download.csv', encoding:str="utf-8-sig") -> StreamingResponse:
    output = BytesIO()
    df = pd.DataFrame(data)
    df.to_csv(output, index=False, encoding=encoding)
    output.seek(0)
    headers = {"content-type": "application/vnd.ms-excel",
               "content-disposition": 'attachment;filename={}'.format(quote(file_name))}
    return StreamingResponse(output, media_type='text/csv', headers=headers)


class ExcelTools:
    def __init__(self, columns_map=None, order=None):
        """
        :param columns_map: 列名映射 => {"name":"姓名"，"score":"成绩","sex":"性别"}
        :param order: 列排序列表 => ["name","sex","score"]
        """
        self.columns_map = columns_map
        self.order = order

    def file_to_df(self, excel: SpooledTemporaryFile, skip_rows=0, file_type: str = 'xlsx') -> pd.DataFrame:
        try:
            # 读取Excel文件内容
            excel_content = excel.read()
            # 使用tempfile创建临时文件
            with NamedTemporaryFile(suffix=f'.{file_type}', delete=False) as temp_file:
                temp_filename = temp_file.name
                temp_file.write(excel_content)
            if file_type in ('xlsx', 'xls'):
                df = pd.read_excel(temp_filename, skiprows=skip_rows)
            elif file_type == 'csv':
                # export_csv方法 使用的utf-8'
                df = pd.read_csv(temp_filename, skiprows=skip_rows, encoding='utf-8')
            else:
                raise Exception(f'不支持的文件类型: {file_type}')
            df = df.replace(np.nan, '', regex=True)
            # 去除所有字符串列的前导和尾随空格
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            # 如果存在列名映射字典self.columns_map，则重命名列
            if self.columns_map:
                columns_map = dict(zip(self.columns_map.values(), self.columns_map.keys()))
                df = df.rename(columns=columns_map)
            return df
        finally:
            # 确保临时文件的清理
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def file_to_dict(self, excel, skip_rows=0, file_type: str = 'xlsx') -> List[Dict[str, Any]]:
        """
        文件转Python dict
        :param excel:
        :param skip_rows:
        :param file_type:
        :return:
        """
        if not excel:
            return []
        df = self.file_to_df(excel, skip_rows=skip_rows, file_type=file_type)
        result = df.to_dict(orient='records')
        return result

    def dict_to_excel(self, datas: List[Dict[str, Any]]) -> BytesIO:
        """
        将数据集转换为Excel文件并返回BytesIO对象
        :param datas: 数据集 => [{"name":"张三","score":90，"sex":"男"}]
        :return: BytesIO对象，包含生成的Excel文件内容
        """
        output = BytesIO()
        df = pd.DataFrame(datas)
        if self.order:
            df = df[self.order]
        if self.columns_map:
            df.rename(columns=self.columns_map, inplace=True)
        # 将DataFrame写入Excel文件
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.fillna(' ', inplace=True)
            df.to_excel(writer, sheet_name='sheet1', index=False)
            worksheet = writer.sheets['sheet1']
            # 设置每列的宽度，使其足以容纳该列中最长的字符串长度加上一个额外空间
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)
        output.seek(0)
        return output
