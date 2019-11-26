#!python3

import patches

patches_list = {
    ("js", "entry.js"): [patches.fix_shortcut_settings,
                         patches.fix_duplicate_key_event_handling]
}


def main():
    patches.do_patch(patches_list)


if __name__ == "__main__":
    main()
