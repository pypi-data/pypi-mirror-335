import re
import hashlib
from typing import Union
from importlib import import_module


def md5(text: Union[str, bytes]) -> str:
    if isinstance(text, str):
        text = text.encode('utf-8')
    return hashlib.md5(text).hexdigest()


def build_path(site, url, file_type):
    return f"{site}/{md5(url)}.{file_type}"


def format_size(content_length: int) -> str:
    units = ["KB", "MB", "GB", "TB"]
    for i in range(4):
        num = content_length / (1024 ** (i + 1))
        if num < 1024:
            return f"{round(num, 2)} {units[i]}"


def dynamic_load_class(model_info):
    if isinstance(model_info, str):
        if "import" in model_info:
            model_path, class_name = re.search(
                r"from (.*?) import (.*?)$", model_info
            ).groups()
            model = import_module(model_path)
            class_object = getattr(model, class_name)
        else:
            model_path, class_name = model_info.rsplit(".", 1)
            model = import_module(model_path)
            class_object = getattr(model, class_name)
        return class_object
    raise TypeError()


# def download_log_info(item:dict) -> str:
#     return "\n".join([" " * 12 + f"{str(k).ljust(14)}:    {str(v)}" for k, v in item.items()])
