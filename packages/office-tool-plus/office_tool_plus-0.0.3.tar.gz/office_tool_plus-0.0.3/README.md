# 安装

```shell
pip install office-tool-plus -i https://mirrors.aliyun.com/pypi/simple/
```

# 使用

## excel

### ws_to_pdf(excel_path, sheet_names=None, pdf_dir=None):

> 将指定 Excel 工作簿中的工作表导出为PDF格式。

**参数：**

- `excel_path`: Excel 文件的路径。
- `sheet_names`: 需要导出的工作表名称列表。如果未提供，则默认导出所有工作表。
- `pdf_dir`: PDF 文件的保存目录。如果未提供，则默认保存在 Excel 文件的同目录下。

**返回：**

- `pdf_path`: 导出的PDF文件路径。

**示例：**

```shell
from office_tool_plus import ExcelTools

excel = ExcelTools()
# 将整个Excel导出为pdf，并保存在源目录下
excel.ws_to_pdf('test.xlsx')
# 将整个Excel导出为pdf，并保存在output目录下
excel.ws_to_pdf('test.xlsx', pdf_dir='output')
# 将指定sheet导出为pdf，并保存在源目录下
excel.ws_to_pdf('test.xlsx', ['Sheet1', 'Sheet2'])
# 将指定sheet导出为pdf，并保存在output目录下
excel.ws_to_pdf('test.xlsx', ['Sheet1', 'Sheet2'], 'output')
```

### wb_to_pdf(excel_dir, recursive=True, suffix=None, pdf_dir=None):

> 将指定目录下的Excel文件批量导出为PDF格式。

**参数：**

- `excel_dir`: Excel 文件的目录路径。
- `suffix`: 需要导出的文件后缀名列表。如果未提供，则默认导出`["*.xlsx", "*.xls"]`
- `recursive`: 是否递归搜索子目录。如果为True，则递归搜索子目录，否则只搜索当前目录。
- `pdf_dir`: PDF 文件的保存目录。如果未提供，则默认保存在 Excel 文件的同目录下。

**返回：**

- `None`

**示例：**

```shell
from office_tool_plus import ExcelTools

excel = ExcelTools()
# 将 test 目录下（包含子目录）所有的 Excel 文件批量导出为pdf，并保存在源目录下
excel.wb_to_pdf('test')
# 将 test 目录下（包含子目录）所有的 Excel 文件批量导出为pdf，并保存在 output 目录下
excel.wb_to_pdf('test', pdf_dir='output')
# 将 test 目录下（不包含子目录）所有的 Excel 文件批量导出为pdf，并保存在源目录下
excel.wb_to_pdf('test', recursive=False)
# 将 test 目录下（不包含子目录）,后缀是 *.xlsx 的 Excel 文件批量导出为pdf，并保存在 output 目录下
excel.wb_to_pdf('test', recursive=False, suffix=['*.xlsx'], pdf_dir='output')
```
