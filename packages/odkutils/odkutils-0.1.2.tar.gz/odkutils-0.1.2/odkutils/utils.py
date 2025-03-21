import os
from typing import Optional
import zipfile
from .caj2pdf import CAJParser

# 解压ZIP文件到指定目录
def unzip_file(zip_path: str, extract_to: str) -> Optional[Exception]:
    """
    解压 ZIP 文件到指定目录
    :param zip_path: ZIP 文件路径
    :param extract_to: 解压到的目标目录
    """
    try:
        os.makedirs(extract_to, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 安全解压：校验每个文件路径
            for file_info in zip_ref.infolist():
                # 防御目录遍历攻击
                target_path = os.path.normpath(os.path.join(extract_to, file_info.filename))
                if not os.path.commonprefix([target_path, os.path.abspath(extract_to)]) == os.path.abspath(extract_to):
                    raise ValueError(f"非法文件路径: {file_info.filename}")
                
            # 完成校验后执行解压
            zip_ref.extractall(extract_to)
            return None
    except (zipfile.BadZipFile, FileNotFoundError, ValueError) as e:
        return e
    except Exception as e:
        return e

# caj2pdf caj转为pdf 
def convert_caj2pdf(input_file, output_file)-> Optional[Exception]:
    try:
        caj = CAJParser(input_file)
        caj.convert(output_file)
        return None
    except Exception as e:
        return e

