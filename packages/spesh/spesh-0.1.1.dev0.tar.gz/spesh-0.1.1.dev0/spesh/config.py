#!/usr/bin/env python3
import os

DEBUG = False

TOP = None # topbar object

def get_terminal_columns():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80  # Default fallback width

# ------------------------------- this always breaks
# import sys, tty, termios
# def get_cursor_position():
#     stdin = sys.stdin
#     stdout = sys.stdout

#     # Save terminal settings
#     old_settings = termios.tcgetattr(stdin)
#     try:
#         # Set terminal to raw mode
#         tty.setcbreak(stdin.fileno())

#         # Write the ANSI escape code to query cursor position
#         stdout.write("\x1b[6n")
#         stdout.flush()

#         # Read response: ESC [ row ; col R
#         response = ""
#         while True:
#             char = stdin.read(1)
#             if char == "R":
#                 break
#             response += char
#     finally:
#         # Restore terminal settings
#         termios.tcsetattr(stdin, termios.TCSADRAIN, old_settings)

#     # Parse the row and column from the response
#     _, position = response.split("[")
#     row, col = map(int, position.split(";"))
#     return row, col

# #print(get_cursor_position())
