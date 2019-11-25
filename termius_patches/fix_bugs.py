#!python3

import sys
import json
import re
import logging

from patch_asar import PatchAsar


def regex_find(js_content, pattern, occurrences=1):
    logging.info(f"查找：{pattern}")
    match_result = re.findall(pattern.encode("utf-8"), js_content)
    if len(match_result) != occurrences:
        raise Exception(f"找不到`{pattern}`，可能补丁已执行过，或者需要更新补丁脚本。")
    else:
        return match_result[0]


def add_dev_console_switch(js_content):
    pattern = r"this\.browserWindow=new .\.BrowserWindow\(.\)," + \
              r".\.manage\(this\.browserWindow\);"
    append = b"""
        if (process.argv.length > 0 && process.argv[0] == "dev")
            this.browserWindow.webContents.openDevTools();
        """
    found = regex_find(js_content, pattern)
    return js_content.replace(found, found + append, 1)


def fix_shortcut_settings(js_content):
    pattern = r"buildListOfTypeSpecificShortcutArgs\(.\){.*}"

    found = regex_find(js_content, pattern)

    sub_find = r"this\.availableActions\(\)"
    sub_replace = b"this.availableActions(true)"
    sub_found = regex_find(found, sub_find, 2)

    patched = found.replace(sub_found, sub_replace, 2)
    return js_content.replace(found, patched)


def fix_duplicate_key_event_handling(js_content):
    pattern = r"this\._customKeyEventHandler&&!1===" \
              r"this\._customKeyEventHandler\(.\)\|\|"
    found = regex_find(js_content, pattern)
    patched = b"/*{" + found + b"}*/"
    return js_content.replace(found, patched, 1)


def do_patch(patches):
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)-6s %(message)s")
    patch = PatchAsar(logger=logging)
    for file_path in patches:
        content = patch.get_file_content(file_path)
        for patch_func in patches[file_path]:
            content = patch_func(content)
        patch.update_file(file_path, content)
    patch.make_backup()
    patch.write_asar_file()
    logging.info("完成！")
