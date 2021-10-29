import tarfile
from typing import List, Dict

from client.config import EXCLUDE_DIRS, EXCLUDE_SUFFIX


def make_targz(output_filename, includes: List[str], fe_dist_mapping: Dict[str, str] = None) -> bool:
    """
    一次性打包目录为tar.gz
    :param output_filename: 压缩文件名
    :param includes: 需要被打包进去的白名单目录
    :param fe_dist_mapping: 前端本地目录和部署目录的映射
    :return: bool
    """

    excludes = [item.strip() for item in EXCLUDE_DIRS.split(',')] if EXCLUDE_DIRS else []
    exclude_suffixes = [item.strip() for item in EXCLUDE_SUFFIX.split(',')] if EXCLUDE_SUFFIX else []

    def exclude_function(tarinfo):
        file_path = tarinfo.name
        if _check_ignore(file_path, excludes, exclude_suffixes):
            return None
        else:
            print(file_path)
            return tarinfo
    with tarfile.open(output_filename, "w:gz") as tar:
        for file_path in includes:
            tar.add(file_path, filter=exclude_function)
        for dist, mapping_dist in (fe_dist_mapping or {}).items():
            tar.add(dist, arcname=mapping_dist, filter=exclude_function)
    return True


def _check_ignore(file_path: str, excludes: List[str], exclude_suffixes: List[str]) -> bool:
    if not file_path:
        return True
    for path in excludes:
        if file_path == path:
            return True
    for suffix in exclude_suffixes:
        if file_path.endswith(suffix):
            return True
    return False
