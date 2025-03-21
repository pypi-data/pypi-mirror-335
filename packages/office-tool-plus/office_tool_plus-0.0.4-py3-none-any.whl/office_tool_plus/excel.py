from .utils import *


class ExcelTools:
    def __init__(self):
        self.app = None

    def create_app(self):
        from win32com.client import gencache
        self.app = gencache.EnsureDispatch("Excel.Application")
        self.app.Visible = False

    def close_app(self):
        self.app.Quit()
        self.app = None

    def ws_to_pdf(self, excel_path: str, sheet_names: list = None, pdf_dir: str = None):
        """
        将指定的Excel工作簿导出为PDF格式。

        参数:
        - excel_path: str, Excel文件的路径。
        - sheet_names: list, 需要导出的工作表名称列表。如果未提供，则默认导出所有工作表。
        - pdf_dir: str, PDF文件的保存目录。如果未提供，则默认保存在Excel文件的同目录下。

        返回:
        - pdf_path: 导出的PDF文件路径。
        """

        # 检查并准备文件路径
        excel_path = check_file_path(excel_path)
        pdf_path = save_file_path(excel_path, "output", pdf_dir)

        # 如果没有提供特定的工作表名称，则导出所有工作表
        if self.app is None:
            self.create_app()

        # 打开Excel工作簿
        workbook = self.app.Workbooks.Open(excel_path)

        # 确定需要导出的工作表名称列表
        sheet_names = sheet_names or [sheet.Name for sheet in workbook.Sheets]

        # 识别出需要隐藏的工作表
        sheets_to_hide = [sheet for sheet in workbook.Sheets if sheet.Name not in sheet_names]
        # 临时隐藏不需要导出的工作表
        for sheet in sheets_to_hide:
            sheet.Visible = False

        try:
            # 导出可见的工作表为PDF
            workbook.ExportAsFixedFormat(0, str(pdf_path))
        except Exception as e:
            print(f"导出工作表到PDF时出错：{e}")

        # 恢复所有工作表的可见性
        for sheet in sheets_to_hide:
            sheet.Visible = True
        # 关闭工作簿时不保存更改
        workbook.Close(SaveChanges=False)
        # 退出Excel应用程序
        self.app.Quit()
        self.app = None
        # 返回导出的PDF文件路径
        return pdf_path

    def wb_to_pdf(self, excel_dir: str, suffix: list = None, recursive=True, pdf_dir: str = None):
        """
        将指定目录下的Excel文件转换为PDF格式。

        参数:
        - excel_dir: str,  Excel文件所在目录
        - pdf_dir: str, PDF文件的保存目录。如果未提供，则默认保存在Excel文件的同目录下。
        """
        suffix = suffix or ["*.xlsx", "*.xls"]
        excel_path_yield = search_files(excel_dir, suffix, recursive)
        if self.app is None:
            self.create_app()
        for excel_path in excel_path_yield:
            # 检查并准备文件路径
            pdf_path = save_file_path(excel_path, ".pdf", pdf_dir)
            # 打开Excel工作簿
            workbook = self.app.Workbooks.Open(excel_path)
            try:
                # 导出可见的工作表为PDF
                workbook.ExportAsFixedFormat(0, str(pdf_path))
            except Exception as e:
                print(f"导出工作表到PDF时出错：{e}")
            # 关闭工作簿时不保存更改
            workbook.Close(SaveChanges=False)

        # 退出Excel应用程序
        self.app.Quit()
        self.app = None


if __name__ == '__main__':
    pass
