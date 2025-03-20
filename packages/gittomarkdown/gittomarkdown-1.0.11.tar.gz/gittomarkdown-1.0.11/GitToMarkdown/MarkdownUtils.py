import json
import os
from pathlib import Path
import pkg_resources
from .ext import ext
class Markdown:
    
    EXT_MAP =ext

    def __init__(self, filename) -> None:
        if not os.path.exists("./Output"):
            os.makedirs("./Output")
        self.handle = open(filename, "w", encoding="utf-8")

    def add_header(self, content, level=1):
        if level > 6:
            raise ValueError("Header level must be between 1 and 6.")
        self.handle.write("#" * level + " " + content + "\n")

    def add_code_block(self, content, fileext):
        ext = ""
        if fileext.lower() in self.EXT_MAP:
            ext = self.EXT_MAP[fileext.lower()]
        ctx = f"""\n```{ext}\n{content}\n```\n"""
        self.handle.write(ctx)

    def add_para(self, content):
        self.handle.write(content)
