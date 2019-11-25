#!python3

import fix_bugs

patches = {
    ("js", "entry.js"): [fix_bugs.fix_shortcut_settings,
                         fix_bugs.fix_duplicate_key_event_handling],
    ("js", "main.js"): [fix_bugs.add_dev_console_switch]
}


def main():
    fix_bugs.do_patch(patches)


if __name__ == "__main__":
    main()
