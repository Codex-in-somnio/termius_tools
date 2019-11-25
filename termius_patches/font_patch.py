import sys
import json
import re

from patch_asar import PatchAsar

DEFAULT_FALLBACK = "Microsoft YaHei"
DEFAULT_ADD = "Source Code Pro, Microsoft YaHei"
SEARCH_KEY_FONT = "Source Code Pro"


def die(msg):
    print(f"发生了错误：{msg}")
    input()
    sys.exit(1)


def edit_font_list(font_list_str):
    font_list = json.loads(font_list_str)
    while True:
        print("======================")
        print("当前字体列表：")
        for i in range(len(font_list)):
            print(f"{i:2}  {font_list[i]}")
        print("======================")
        print("请输入一个选项：")
        print("a - 添加新的字体")
        print("f - 给一个现有字体加上后备字体")
        print("b - 批量给现有字体加上后备字体")
        print("d - 删除一个字体")
        print("x - 执行")
        print("q - 退出")

        option = input("> ").lower()

        def enter_number(prompt):
            num = input(prompt)
            if not re.match(r"^[0-9]*$", num):
                print("输入有误。")
                return False
            num = int(num)
            if num >= len(font_list):
                print("输入超出范围。")
                return False
            return num

        def add_font(font):
            if font in font_list:
                print(f"字体选项已存在：{font}")
            else:
                font_list.append(font)

        if option == "a":
            new_font = input(f"请输入新的字体选项（默认：'{DEFAULT_ADD}'）：")
            if new_font == "":
                new_font = DEFAULT_ADD
            add_font(new_font)
        elif option == "f" or option == "b":
            fallback_font = input(
                f"请输入后备字体名（默认：'{DEFAULT_FALLBACK}'）：")
            if fallback_font == "":
                fallback_font = DEFAULT_FALLBACK
            if option == "f":
                font_num = enter_number("请输入要增加后备字体的字体序号：")
                if font_num is not False:
                    new_font = f"{font_list[font_num]}, {fallback_font}"
                    add_font(new_font)
            elif option == "b":
                for font in font_list[:]:
                    if font.find(",") != -1:
                        continue
                    new_font = f"{font}, {fallback_font}"
                    add_font(new_font)
        elif option == "d":
            del_num = enter_number("请输入要删除的字体序号：")
            if del_num is not False:
                if del_num == 0:
                    print("此选项用于查找定位，不能删除。")
                    continue
                font_list.remove(font_list[del_num])
        elif option == "x":
            return json.dumps(font_list).encode("utf-8")
        elif option == "q":
            sys.exit(0)


def find_font_list(js_content):
    pattern = re.compile(
        r'\["{}"[A-Za-z-," ]*\]'.format(SEARCH_KEY_FONT).encode("utf-8"))
    match_result = pattern.findall(js_content)
    if len(match_result) != 1:
        die("找不到替换目标，可能需要更新补丁脚本。")
    return match_result[0]


def do_font_patch(patch):
    js_file_path = ["js", "entry.js"]
    js_content = patch.get_file_content(js_file_path)
    font_list = find_font_list(js_content)
    new_font_list = edit_font_list(font_list)
    patched_js_content = js_content.replace(font_list, new_font_list, 1)
    patch.update_file(js_file_path, patched_js_content)


def main():
    try:
        patch = PatchAsar()
    except ValueError as e:
        die(e)

    do_font_patch(patch)

    try:
        asar_backup = patch.make_backup()
        print(f"即将修改文件'{patch.asar_file_path}'。"
              f"该文件的备份'{asar_backup}'已保存在工作目录中。")
        print("=================")

        patch.write_asar_file()
    except OSError as e:
        die(e)

    print("完成！")
    input()


if __name__ == "__main__":
    main()
