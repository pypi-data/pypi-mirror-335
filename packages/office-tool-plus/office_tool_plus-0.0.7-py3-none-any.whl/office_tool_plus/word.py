from .utils import *
from win32com.client import constants, gencache


class WordTools:
    def __init__(self):
        self.app = None

    def create_app(self):
        self.app = gencache.EnsureDispatch("Word.Application")
        self.app.Visible = False

    def close_app(self):
        self.app.Quit()
        self.app = None

    def single_to_pdf(self, word_path: str, pdf_dir: str = None):
        """
        将单个Word文档转换为PDF格式。

        :param word_path: Word文档的文件路径。
        :param pdf_dir: PDF文件的保存目录，如果未提供，则默认保存在Word文档的同目录下。
        :return: 转换后的PDF文件路径。
        """
        # 检查并准备文件路径
        word_path = check_file_path(word_path)
        pdf_path = save_file_path(word_path, ".pdf", pdf_dir)

        # 如果没有提供特定的工作表名称，则导出所有工作表
        if self.app is None:
            self.create_app()
        # 打开Word文档，设置为只读模式
        doc = self.app.Documents.Open(str(word_path), ReadOnly=1)

        try:
            # 将Word文档导出为PDF格式
            doc.ExportAsFixedFormat(pdf_path, constants.wdExportFormatPDF)
        except Exception as e:
            print(f"导出word到PDF时出错：{e}")

        # 关闭时不保存更改
        doc.Close(SaveChanges=False)

        # 退出应用程序
        self.app.Quit()
        self.app = None

        # 返回导出的PDF文件路径
        return pdf_path

    def many_to_pdf(self, word_dir: str, suffix: list = None, recursive=True, pdf_dir: str = None):
        """
        将指定目录下的Excel文件转换为PDF格式。

        参数:
        - word_dir: str,  Word 文件所在目录
        - pdf_dir: str, PDF文件的保存目录。如果未提供，则默认保存在Excel文件的同目录下。
        """
        suffix = suffix or ["*.doc", "*.docx"]
        word_path_yield = search_files(word_dir, suffix, recursive)
        if self.app is None:
            self.create_app()
        for word_path in word_path_yield:
            # 检查并准备文件路径
            pdf_path = save_file_path(word_path, ".pdf", pdf_dir)
            # 打开Word文档，设置为只读模式
            doc = self.app.Documents.Open(str(word_path), ReadOnly=1)
            try:
                # 将Word文档导出为PDF格式
                doc.ExportAsFixedFormat(pdf_path, constants.wdExportFormatPDF)
            except Exception as e:
                print(f"导出word到PDF时出错：{e}")

            # 关闭时不保存更改
            doc.Close(SaveChanges=False)

        # 退出Excel应用程序
        self.app.Quit()
        self.app = None
