#!/bin/bash

pyinstaller -c -F --clean --name run-server-x86_64-unknown-linux-gnu pyrb/controllers/api/main.py
