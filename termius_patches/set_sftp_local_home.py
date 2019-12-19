#!python3

import patches
import re
import logging
import argparse

PATTERN = \
    rb'(getHomePath\(\){return process\.env\.HOME\?process\.env\.HOME:"([^"]+)"})'

JS_PATH = ("js", "entry.js")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="修改Termius的SFTP本地HOME目录")
    parser.add_argument("home", metavar="PATH", nargs="?",
                        help="要设置的SFTP本地HOME目录路径（不给此参数则仅读取）")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s:%(message)s")

    patch = patches.PatchAsar(logger=logging)

    content = patch.get_file_content(JS_PATH)
    result = re.findall(PATTERN, content)
    if len(result) != 1:
        logging.error("找不到查找目标。")
        exit(-1)
    orig_get_home_path = result[0][0]
    current_home = result[0][1].decode("utf-8")
    logging.info(f'当前SFTP的HOME目录路径："{current_home}"')

    if not args.home:
        exit()

    new_home_path = args.home.replace('"', '\\"')
    logging.info(f"新的HOME目录路径：{new_home_path}")

    new_get_home_path = \
        b'getHomePath(){return process.env.HOME?process.env.HOME:"' + \
        new_home_path.encode("utf-8") + b'"}'

    content = content.replace(orig_get_home_path, new_get_home_path)
    patch.update_file(JS_PATH, content)
    patch.make_backup()
    patch.write_asar_file()
