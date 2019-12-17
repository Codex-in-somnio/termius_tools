#!python3

from patches import patches
from patches import do_patch

patches_list = {
    ("js", "main.js"): [patches.add_dev_console_switch],
    ("js", "entry.js"): [patches.add_enter_to_connect,
                         patches.add_arrowdown_shortcut_connect,
                         patches.add_tab_highlight_js],
    ("style.css",): [patches.add_tab_highlight_css]
}


def main():
    do_patch(patches_list)


if __name__ == "__main__":
    main()
