import time
import logging
from nicegui import ui, App

LOG_TAG = "FMS UI"

uilog = None

def registerLog():
    global uilog
    uilog = ui.log(max_lines=100).classes('w-6xl')

def log(level: int, tag: str, message: str):
    logging.getLogger(tag).log(level, message)
    if level != logging.DEBUG and uilog != None:
        uilog.push(f"[{logging.getLevelName(level)} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] {tag}: {message}")

def injectCSS():
    ui.add_css('''
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap');
        body {
            font-family: 'JetBrains Mono', monospace;
        }
    ''')