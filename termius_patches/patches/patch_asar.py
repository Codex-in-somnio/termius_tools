import struct
import json
import os
import sys
import time
import shutil
import re
import json
import logging


class PatchAsar:
    asar_file_path = os.getenv("LocalAppData") + \
        "\\Programs\\Termius\\resources\\app.asar"

    backup_filename_base = "app.asar.bak"

    def __init__(self, logger=None):
        if logger is not None:
            self.logger = logger
        else:
            self.logger = getLogger()

        self.logger.info(f"打开ASAR：{self.asar_file_path}")
        with open(self.asar_file_path, "rb") as asar_file:
            asar_file.seek(4)
            header_len = struct.unpack("<I", asar_file.read(4))[0]
            asar_file.seek(8)
            header_json_bytes = asar_file.read(header_len)[8:]
            header_json_bytes = header_json_bytes.split(b'\0', 1)[0]
            try:
                self.header = json.loads(header_json_bytes)
            except ValueError as e:
                self.logger.trace(header_json_bytes)
                self.logger.error("解析JSON失败")
                raise e

            asar_file.seek(8 + header_len)
            self.body = asar_file.read()

    def make_backup(self):
        backup_filename = "{}.{}".format(
            self.backup_filename_base,
            str(int(time.time())))
        try:
            self.logger.info(f"创建备份：{backup_filename}")
            shutil.copyfile(self.asar_file_path, backup_filename)
        except OSError as e:
            self.logger.error(
                f"尝试创建备份时发生了错误。"
                f"请检查文件'{self.asar_file_path}'可以访问，"
                f"且工作目录可写。")
            raise e
        return backup_filename

    def get_file_obj(self, file_path):
        file_obj = self.header
        for name in file_path:
            file_obj = file_obj["files"][name]
        return file_obj

    def get_file_loc_length(self, file_path):
        file_obj = self.get_file_obj(file_path)
        loc = int(file_obj["offset"])
        length = int(file_obj["size"])
        return loc, length

    def get_file_content(self, file_path):
        loc, length = self.get_file_loc_length(file_path)
        file_content = self.body[loc: loc + length]
        return file_content

    def update_file(self, file_path, new_content):
        loc, length = self.get_file_loc_length(file_path)
        self.body = self.body[:loc] + \
            new_content + self.body[loc+length:]

        file_obj = self.get_file_obj(file_path)

        new_length = len(new_content)
        file_obj["size"] = new_length
        PatchAsar.update_header(self.header, loc, new_length - length)

    @staticmethod
    def update_header(header, loc, diff):
        for key in header:
            if key == "offset":
                offset = int(header["offset"])
                if offset > loc:
                    header["offset"] = str(offset + diff)
            elif key != "size" and key != "executable" and key != "unpacked":
                # print(key)
                PatchAsar.update_header(header[key], loc, diff)

    def regenerate_header(self):
        header_json_bytes = json.dumps(self.header).encode("ascii")

        def int_to_bytes(num):
            return num.to_bytes(4, byteorder='little', signed=False)
        len4 = int_to_bytes(len(header_json_bytes))
        len3 = int_to_bytes(len(header_json_bytes) + 6)
        len2 = int_to_bytes(len(header_json_bytes) + 10)
        len1 = int_to_bytes(len(len2))
        suf = b"\00\00"
        return len1 + len2 + len3 + len4 + header_json_bytes + suf

    def write_asar_file(self):
        new_asar_content = self.regenerate_header() + self.body
        try:
            self.logger.info(f"写入ASAR：{self.asar_file_path}")
            with open(self.asar_file_path, "wb") as asar_file:
                asar_file.write(new_asar_content)
        except OSError as e:
            self.logger.error(f"写入文件'{self.asar_file_path}'失败。")
            raise e


def getLogger(debug=True):
    logger = logging.getLogger("termius_patches")
    formatter = logging.Formatter("%(levelname)-6s %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger


def do_patch(patches):
    """
    传入一个字典：{(文件路径元组): patches里定义的补丁函数}
    """
    logger = getLogger()
    patch = PatchAsar(logger=logger)
    for file_path in patches:
        content = patch.get_file_content(file_path)
        for patch_func in patches[file_path]:
            content = patch_func(content)
        patch.update_file(file_path, content)
    patch.make_backup()
    patch.write_asar_file()
    logging.info("完成！")
