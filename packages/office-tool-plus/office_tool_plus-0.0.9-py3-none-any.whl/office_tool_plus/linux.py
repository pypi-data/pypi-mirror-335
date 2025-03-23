from .utils import *
import subprocess


@check_platform('linux')
def libreoffice(input_path, convert_to, output_dir=None, java_home=None, lang=None):
    """
    使用LibreOffice在Linux平台上转换文档格式。
    需要安装 apk add libreoffice openjdk8 font-noto-cjk
        - libreoffice ：用于处理Office文件。
        - openjdk8 ：用于运行LibreOffice。
        - font-noto-cjk ：用于支持中文字体。

    参数:
    - input_path: 输入文件的路径。
    - convert_to: 要转换的文件格式。
    - output_dir: 转换后的文件输出目录。
    - java_home: （可选）Java安装目录的路径，默认使用'/usr/bin/java'。
    - lang: （可选）设置LANG环境变量，默认为'zh_CN.UTF-8'。

    此函数不返回任何值。
    """

    input_path = check_file_path(input_path)  # 检查文件是否存在
    output_dir = check_folder_path(output_dir or str(input_path.parent))  # 检查目录是否存在

    # 初始化环境变量，以确保LibreOffice能够正确运行
    env = os.environ.copy()
    # 设置JAVA_HOME环境变量，指向Java安装目录
    env['JAVA_HOME'] = java_home or '/usr/bin/java'  # 修改此路径为你的Java安装路径
    # 设置LANG环境变量，以支持文档中的UTF-8编码
    env['LANG'] = lang or 'zh_CN.UTF-8'  # 设置LANG环境变量以支持UTF-8编码

    # 执行LibreOffice命令行工具来转换文档
    subprocess.run([
        'libreoffice', '--headless',
        '--convert-to', convert_to,
        '--outdir', output_dir,
        input_path
    ], check=True, env=env)
