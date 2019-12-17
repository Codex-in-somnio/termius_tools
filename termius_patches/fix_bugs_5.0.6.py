#!python3

from patches import patches
from patches import do_patch

patches_list = {
    ("js", "entry.js"): [patches.fix_shortcut_settings,
                         patches.fix_duplicate_key_event_handling]
}


def main():
    do_patch(patches_list)


if __name__ == "__main__":
    main()
