#!/usr/bin/env python3
import os

DEBUG = False


def get_terminal_columns():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80  # Default fallback width
