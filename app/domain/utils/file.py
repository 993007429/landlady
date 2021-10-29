import os


def gen_file_structure(startpath: str) -> str:
    result = ''
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        result += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            result += '{}{}\n'.format(subindent, f)
    return result
