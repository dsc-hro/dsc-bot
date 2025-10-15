#!/usr/bin/env bash

"""
Simple HTML Parser to extract GladOS voice lines from the Portal Wiki.
"""

import json

from html.parser import HTMLParser
from argparse import ArgumentParser
from pathlib import Path
from urllib import request

portal_wiki_url = "https://theportalwiki.com/wiki/GLaDOS_voice_lines_(Portal)"


class PortalParser(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.state = "idle"
        self.voice_lines = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.state == "idle":
            if tag == "li":
                self.state = "li"
        elif self.state == "li":
            if tag == "i":
                self.state = "parse"
        return super().handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if self.state == "parse" and tag == "i":
            self.state = "idle"
        return super().handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if self.state == "parse":
            self.voice_lines.append(data)
        return super().handle_data(data)


if __name__ == "__main__":
    arg_parser = ArgumentParser(description="parse GlaDOS voice lines from portal wiki")

    # arg_parser.add_argument("input", type=Path)
    args = arg_parser.parse_args()

    response = request.urlopen(portal_wiki_url).read().decode("utf-8")

    parser = PortalParser()
    parser.feed(response)

    with open("output.json", "w") as file:
        json.dump(parser.voice_lines, file)

    print(parser.voice_lines)
