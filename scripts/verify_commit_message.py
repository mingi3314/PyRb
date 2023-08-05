#!/usr/bin/python3

import re
import sys

COMMIT_MESSAGE_REGEX = (
    r'^((Revert ")?(feat|fix|docs|style|refactor|perf|test|ci|build|chore)'
    r"(\(.*\))?!?:\s.{1,50})"
)


def validate_commit_message(message: str) -> bool:
    """
    Function to validate the commit message
    Args:
        message (str): The message to validate
    Returns:
        bool: True for valid messages, False otherwise
    """
    if not re.match(COMMIT_MESSAGE_REGEX, message):
        # fmt: off
        print("""Your commit message does not match conventional commit format.

Examples:
------------------------

feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files

------------------------

feat(api)!: send an email to the customer when a product is shipped

------------------------

docs: correct spelling of CHANGELOG

------------------------
See COMMIT_CONVENTION from Notion for more details.
https://www.notion.so/thealphaprime/Git-90c251856b6e4e9ea1973034268778d5""")
        # fmt: on
        return False
    return True


def main() -> None:
    message_file = sys.argv[1]
    txt_file = open(message_file)
    commit_message = txt_file.read()

    if not validate_commit_message(commit_message):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
