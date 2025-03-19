#!/usr/bin/env python3
"""Logging utilities for Lambda Deploy."""

import sys
import os
from typing import Optional

# ansi color codes
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'DIM': '\033[2m',
    'ITALIC': '\033[3m',
    'UNDERLINE': '\033[4m',
    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'BRIGHT_BLACK': '\033[90m',
    'BRIGHT_RED': '\033[91m',
    'BRIGHT_GREEN': '\033[92m',
    'BRIGHT_YELLOW': '\033[93m',
    'BRIGHT_BLUE': '\033[94m',
    'BRIGHT_MAGENTA': '\033[95m',
    'BRIGHT_CYAN': '\033[96m',
    'BRIGHT_WHITE': '\033[97m',
    'BG_BLACK': '\033[40m',
    'BG_RED': '\033[41m',
    'BG_GREEN': '\033[42m',
    'BG_YELLOW': '\033[43m',
    'BG_BLUE': '\033[44m',
    'BG_MAGENTA': '\033[45m',
    'BG_CYAN': '\033[46m',
    'BG_WHITE': '\033[47m',
}

# check if colors should be disabled
USE_COLORS = True
if os.environ.get('NO_COLOR') or not sys.stdout.isatty():
    USE_COLORS = False

def colorize(text: str, color: str) -> str:

    if not USE_COLORS:
        return text

    color_code = COLORS.get(color.upper(), '')
    if not color_code:
        return text

    return f"{color_code}{text}{COLORS['RESET']}"

def log(message: str, color: Optional[str] = None, prefix: str = "-> ", error: bool = False) -> None:

    output_stream = sys.stderr if error else sys.stdout

    if color:
        message = colorize(message, color)

    prefix_colored = colorize(prefix, 'BRIGHT_CYAN') if not error else colorize(prefix, 'BRIGHT_RED')

    print(f"{prefix_colored}{message}", file=output_stream)

def debug(message: str) -> None:

    if os.environ.get('DEBUG'):
        log(f"[DEBUG] {message}", color='DIM', prefix="")

def error(message: str) -> None:

    log(message, color='RED', prefix="[ERROR] ", error=True)

def warning(message: str) -> None:

    log(message, color='YELLOW', prefix="[WARNING] ")

def success(message: str) -> None:

    log(message, color='GREEN', prefix="[SUCCESS] ")

def info(message: str) -> None:

    log(message, color='BLUE', prefix="[INFO] ")

def section(title: str) -> None:

    print("")
    log(f"{colorize('━━━', 'BRIGHT_CYAN')} {colorize(title.upper(), 'BOLD')} {colorize('━━━', 'BRIGHT_CYAN')}")
