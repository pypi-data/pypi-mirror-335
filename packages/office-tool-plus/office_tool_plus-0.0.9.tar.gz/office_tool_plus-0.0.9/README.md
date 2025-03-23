# 安装

> `office-tool-plus` 一些自动化办公的工具包

```shell
# 国内源
pip install --upgrade office-tool-plus -i https://mirrors.aliyun.com/pypi/simple/ 
# 官方源（最新版）
pip install --upgrade office-tool-plus -i https://pypi.org/simple  
```

# 使用

## excel

### single_to_pdf(excel_path: str, sheet_names: list = None, pdf_dir: str = None):

> 将指定`Excel`工作簿中的工作表导出为`PDF`格式。

**参数：**

- `excel_path`: `Excel`文件的路径。
- `sheet_names`: 需要导出的工作表名称列表。如果未提供，则默认导出所有工作表。
- `pdf_dir`: `PDF`文件的保存目录。如果未提供，则默认保存在`Excel`文件的同目录下。

**返回：**

- `pdf_path`: 导出的`PDF`文件路径。

**示例：**

```shell
from office_tool_plus import ExcelTools

excel = ExcelTools()
# 将整个 Excel 导出为 pdf，并保存在源目录下
excel.single_to_pdf('test.xlsx')
# 将整个 Excel 导出为 pdf，并保存在 output 目录下
excel.single_to_pdf('test.xlsx', pdf_dir='output')
# 将指定 sheet 导出为 pdf，并保存在源目录下
excel.single_to_pdf('test.xlsx', ['Sheet1', 'Sheet2'])
# 将指定 sheet 导出为 pdf，并保存在 output 目录下
excel.single_to_pdf('test.xlsx', ['Sheet1', 'Sheet2'], 'output')
```

### many_to_pdf(excel_dir: str, suffix: list = None, recursive=True, pdf_dir: str = None):

> 将指定目录下的`Excel`文件批量导出为`PDF`格式。

**参数：**

- `excel_dir`: `Excel`文件的目录路径。
- `suffix`: 需要导出的文件后缀名列表。如果未提供，则默认导出`["*.xlsx", "*.xls"]`
- `recursive`: 是否递归搜索子目录。如果为`True`，则递归搜索子目录，否则只搜索当前目录。
- `pdf_dir`: `PDF`文件的保存目录。如果未提供，则默认保存在`Excel`文件的同目录下。

**返回：**

- `None`

**示例：**

```shell
from office_tool_plus import ExcelTools

excel = ExcelTools()
# 将 test 目录下（包含子目录）所有的 Excel 文件批量导出为 pdf，并保存在源目录下
excel.many_to_pdf('test')
# 将 test 目录下（包含子目录）所有的 Excel 文件批量导出为 pdf，并保存在 output 目录下
excel.many_to_pdf('test', pdf_dir='output')
# 将 test 目录下（不包含子目录）所有的 Excel 文件批量导出为 pdf，并保存在源目录下
excel.many_to_pdf('test', recursive=False)
# 将 test 目录下（不包含子目录）,后缀是 *.xlsx 的 Excel 文件批量导出为 pdf，并保存在 output 目录下
excel.many_to_pdf('test', suffix=['*.xlsx'], recursive=False, pdf_dir='output')
```

## word

### single_to_pdf(word_path: str, pdf_dir: str = None):

> 将指定的`Word`文档导出为`PDF`格式。

**参数：**

- `word_path`: `Word`文件的路径。
- `pdf_dir`: `PDF`文件的保存目录。如果未提供，则默认保存在`Word`文件的同目录下。

**返回：**

- `pdf_path`: 导出的`PDF`文件路径。

**示例：**

```shell
from office_tool_plus import WordTools

word = WordTools()
# 将指定的 Word 导出为 pdf，并保存在源目录下
word.single_to_pdf('test.docx')
# 将指定的 Word 导出为 pdf，并保存在 output 目录下
word.single_to_pdf('test.docx', pdf_dir='output')
```

### many_to_pdf(word_dir: str, suffix: list = None, recursive=True, pdf_dir: str = None):

> 将指定目录下的`Word`文件批量导出为`PDF`格式。

**参数：**

- `word_dir`: `Word`文件的目录路径。
- `suffix`: 需要导出的文件后缀名列表。如果未提供，则默认导出`["*.docx", "*.doc"]`
- `recursive`: 是否递归搜索子目录。如果为`True`，则递归搜索子目录，否则只搜索当前目录。
- `pdf_dir`: `PDF`文件的保存目录。如果未提供，则默认保存在`Word`文件的同目录下。

**返回：**

- `None`

**示例：**

```shell
from office_tool_plus import WordTools

word = WordTools()
# 将 test 目录下（包含子目录）所有的 Word 文件批量导出为 pdf ，并保存在源目录下
word.many_to_pdf('test')
# 将 test 目录下（包含子目录）所有的 Word 文件批量导出为 pdf，并保存在 output 目录下
word.many_to_pdf('test', pdf_dir='output')
# 将 test 目录下（不包含子目录）所有的 Word 文件批量导出为 pdf，并保存在源目录下
word.many_to_pdf('test', recursive=False)
# 将 test 目录下（不包含子目录）,后缀是 *.docx 的 Word 文件批量导出为 pdf，并保存在 output 目录下
word.many_to_pdf('test', suffix=['*.docx'], recursive=False, pdf_dir='output')
```

## Linux 系统下转换文件格式

### libreoffice(input_path, convert_to, output_dir=None, java_home=None, lang=None):

> 使用LibreOffice在Linux平台上转换文档格式。 需要安装 apk add libreoffice openjdk8 font-noto-cjk
> - libreoffice ：用于处理Office文件。
> - openjdk8 ：用于运行LibreOffice。
> - font-noto-cjk ：用于支持中文字体。

**参数：**
- input_path: 输入文件的路径。
- convert_to: 转换后的文件格式。
- output_dir: 转换后的文件保存的目录。
- java_home: （可选）Java安装目录的路径，默认使用'/usr/bin/java'。
- lang: （可选）设置LANG环境变量，默认为'zh_CN.UTF-8'。


**返回：**

- `None`

**示例：**

```shell
from office_tool_plus import libreoffice

# 将 test.xlsx 文件 导出为 pdf ，并保存在源目录下
libreoffice("test.xlsx", "pdf")
# 将 test.xlsx 文件 导出为 pdf ，并保存在 output 目录下
libreoffice("test.xlsx", "pdf", output_dir='output')
# 将 test.docx 文件 导出为 pdf ，并保存在 output 目录下
libreoffice("test.docx", "pdf", output_dir='output')
```
