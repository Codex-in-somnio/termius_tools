import sys
import json
import re
import logging

from patches.patch_asar import PatchAsar

logger = logging.getLogger("termius_patches")


def regex_find(js_content, pattern, occurrences=1):
    logger.info(f"查找：{pattern}")
    match_result = re.findall(pattern.encode("utf-8"), js_content)
    if len(match_result) != occurrences:
        raise Exception(f"找不到`{pattern}`，可能补丁已执行过，或者需要更新补丁脚本。")
    else:
        return match_result[0]


def remove_linebreaks(input_bytes):
    return input_bytes.replace(b"\n", b"").replace(b"\r", b"")


def add_dev_console_switch(js_content):
    pattern = r"this\.browserWindow=new .\.BrowserWindow\(.\)," + \
        r".\.manage\(this\.browserWindow\);"
    append = b"""
        if (process.argv.length > 1 && process.argv[1] == "dev")
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


def add_enter_to_connect(js_content):
    # 一直启用connect按钮
    pattern_1 = r'disabled:!\("ssh"===.\.substring\(0,3\)\),'
    found_1 = regex_find(js_content, pattern_1)
    js_content = js_content.replace(found_1,
                                    b"/*" + found_1 + b"*/")

    # 输入label直接连接
    pattern_2 = r"this,\"quickConnect\",.=>{.\.preventDefault\(\);" \
        r"try{this\.connectToHost\(function\(.\){const .=..\(\)\(" \
        r".\.trim\(\)\.split\(\/\\s\+\/\)\),.=new ..;"

    found_2 = regex_find(js_content, pattern_2)
    sub_pat_1 = b".preventDefault();"
    sub_pat_1_append = b"let hosts = this.props.hosts;"
    replace_2 = found_2.replace(sub_pat_1, sub_pat_1 + sub_pat_1_append)
    var_name = re.search(b"const (.)", found_2).group(1)
    pattern_2_append = remove_linebreaks(b"""
        var target_host;
        if (#._.length == 1) {
            for (const host of hosts) {
                if (host.label.toLowerCase() == #._[0].toLowerCase()) {
                    return host;
                }
            }
        }
        """.replace(b"#", var_name))
    replace_2 += pattern_2_append
    js_content = js_content.replace(found_2, replace_2)
    return js_content


def add_tab_highlight_js(js_content):
    js_content += remove_linebreaks(b"""
        document.addEventListener("keydown", (e) => {
            if (e.code == "Tab") {
                document.body.classList.add("indicate-tab");
            } 
        });

        document.addEventListener("mousedown", (e) => {
            document.body.classList.remove("indicate-tab");
        });
        """)
    return js_content


def add_tab_highlight_css(css_content):
    css_content += remove_linebreaks(b"""
        .indicate-tab *:focus {
            box-shadow:inset 0 0 8px Highlight !important;
        }
        """)
    return css_content


def add_arrowdown_shortcut_connect(js_content):
    pattern = r'placeholder:"Find a host or ssh user@hostname\.\.\.",'
    found = regex_find(js_content, pattern)
    append = remove_linebreaks(b"""
        onKeyDown: event => {
            if (event.keyCode == 40) {
                var listDiv = event.target.parentNode.parentNode.parentNode.nextSibling.nextSibling.querySelector(".ReactVirtualized__Grid");
                var firstSession = listDiv.children[0].children[1].children[0];
                listDiv.focus();
                firstSession.click();
                event.preventDefault();
            }
        },
        """)
    return js_content.replace(found, found + append, 1)
