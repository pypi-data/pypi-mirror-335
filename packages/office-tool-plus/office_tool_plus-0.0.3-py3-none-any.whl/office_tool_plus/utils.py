import os
from pathlib import Path


def unique_file_path(file_path):
    """
    确保文件路径唯一，若存在同名文件则在文件名后添加序号
    参数:
        file_path  原始文件路径
    返回:
        str - 唯一的文件路径
    """
    # 分离文件路径的基名和扩展名
    base, ext = os.path.splitext(file_path)
    # 初始化计数器，用于在文件名后添加序号
    counter = 1
    # 当文件路径已存在时，生成新的唯一文件路径
    while os.path.exists(file_path):
        # 在文件名后添加序号，并更新文件路径
        file_path = f"{base}_{counter}{ext}"
        # 序号递增，以确保文件路径的唯一性
        counter += 1
    # 返回最终确定的唯一文件路径
    return file_path


def check_file_path(file_path):
    """
    验证并返回指定文件路径的绝对路径。

    参数:
        file_path : 待验证的文件路径。

    返回:
        Path: 文件的绝对路径。

    异常:
        ValueError: 如果路径包含非法字符或格式不正确。
        FileNotFoundError: 如果指定的文件路径不存在。
    """
    abs_file_path = Path(file_path).resolve()
    # 确保路径存在且是一个文件
    if not abs_file_path.exists():
        raise FileNotFoundError(f"指定的文件路径 '{abs_file_path}' 不存在。")
    if not abs_file_path.is_file():
        raise ValueError(f"指定的路径 '{abs_file_path}' 不是一个有效的文件。")
    return abs_file_path


def check_folder_path(folder_path):
    """
    验证并返回指定路径的绝对路径，确保其为一个存在的目录。

    参数:
        folder_path: 待验证的目录路径。

    返回:
        Path: 绝对路径对象。

    异常:
        ValueError: 如果输入路径为空或无效。
        FileNotFoundError: 如果指定的路径不存在。
        NotADirectoryError: 如果指定的路径不是一个目录。
    """
    # 检查输入是否为空或无效
    if not folder_path or not isinstance(folder_path, str):
        raise ValueError("输入的路径不能为空或无效。")

    # 解析并验证路径
    abs_folder_path = Path(folder_path).resolve()

    # 检查路径是否存在
    if not abs_folder_path.exists():
        raise FileNotFoundError(f"指定的目录 '{abs_folder_path}' 不存在。")

    # 确保路径是一个目录
    if not abs_folder_path.is_dir():
        raise NotADirectoryError(f"指定的路径 '{abs_folder_path}' 不是一个目录。")

    return abs_folder_path


def save_file_path(input_file, suffix, output_folder=None):
    """
    根据输入文件和后缀生成保存文件的路径。

    参数:
        input_file: 输入文件的路径。
        suffix: 输出文件的后缀。
        output_folder: 输出文件夹路径。默认为 None。

    返回:
        tuple: 包含输入文件的绝对路径和输出文件的绝对路径。
    """
    # 校验 suffix 是否合法
    if not suffix.startswith('.'):
        suffix = f".{suffix}"
    # 获取传入文件的绝对路径
    abs_input_file = check_file_path(input_file)

    # 确保 suffix 合法并生成输出文件路径
    if output_folder is None:
        abs_output_file = abs_input_file.with_suffix(suffix)
    else:
        abs_output_folder = check_folder_path(output_folder)
        abs_output_file = abs_output_folder / f"{abs_input_file.stem}{suffix}"
    # 确保生成的文件路径是唯一的，避免覆盖现有文件
    abs_output_file = unique_file_path(str(abs_output_file))
    return abs_output_file


def search_files(folder, suffix, recursive=True):
    """
    搜索指定文件夹下的文件。

    参数：
    folder : 要搜索的文件夹路径。
    suffix : 文件后缀名模式列表（如['*.txt', '*.csv']）。
    recursive : 是否递归搜索子文件夹。

    返回：
    生成器，逐个返回匹配的文件路径字符串。
    """

    def validate_suffix(input_suffix):
        """验证并规范化suffix参数"""
        if not hasattr(input_suffix, '__iter__') or isinstance(input_suffix, str):
            raise ValueError("suffix 参数必须是可迭代对象（如列表或元组），且不能是单一字符串")
        return input_suffix

    # 参数验证
    suffix = validate_suffix(suffix)
    abs_folder = check_folder_path(folder)
    # 使用Path.rglob进行递归搜索  使用Path.glob仅在给定目录下搜索
    glob_method = abs_folder.rglob if recursive else abs_folder.glob
    for pattern in suffix:
        for file_path in glob_method(pattern):
            yield str(file_path)
