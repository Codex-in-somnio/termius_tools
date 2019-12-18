#!python3

from patches import patches
from patches import do_patch

patches_list = {
    ("js", "entry.js"): [patches.fix_duplicate_key_event_handling,
                         patches.fix_pane2_overflow]
}


def main():
    do_patch(patches_list)


if __name__ == "__main__":
    main()
