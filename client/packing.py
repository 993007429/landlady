import tarfile

from client.config import EXCLUDE_FILES


def make_targz(output_filename, source_dir, arcname):
    """
    一次性打包目录为tar.gz
    :param output_filename: 压缩文件名
    :param source_dir: 需要打包的目录
    :return: bool
    """
    excludes = [item.strip() for item in EXCLUDE_FILES.split(',')]

    def exclude_function(tarinfo):
        names = tarinfo.name.split('/')
        filename = names[1] if len(names) > 1 else ''
        if filename and (filename.startswith('.') or filename in excludes):
            return None
        else:
            return tarinfo
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=arcname, filter=exclude_function)
    return True
