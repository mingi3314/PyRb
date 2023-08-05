#!/bin/bash

set -e

# use pre-commit
pre-commit install

# symlink
ln -sf ../../scripts/verify_commit_message.py .git/hooks/commit-msg

# permission
chmod +x .git/hooks/commit-msg