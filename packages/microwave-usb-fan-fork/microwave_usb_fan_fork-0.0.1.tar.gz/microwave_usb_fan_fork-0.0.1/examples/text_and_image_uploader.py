#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
from dataclasses import dataclass
from pathlib import Path
import click

from json_image import image_message
from microwave_usb_fan_fork import Colour, TextMessage, Program, Device


@dataclass(frozen=True)
class FileMessageTemplate:
    file: Path


@dataclass(frozen=True)
class TextMessageTemplate:
    text: str
    mask: str = None


def manual_parsing(args: list[str]):
    message_templates = []
    i = 0

    while i < len(args):
        if args[i] == '--file':
            # Ensure there's a file argument following the option.
            if i + 1 >= len(args):
                raise click.ClickException("Missing argument for --file")
            file_arg = args[i + 1]
            file_path = Path(file_arg)
            # Check if the file exists, is a file, and is readable.
            if not file_path.exists():
                raise click.ClickException(f"File '{file_path}' does not exist.")
            if not file_path.is_file():
                raise click.ClickException(f"'{file_path}' is not a file.")
            if not os.access(file_path, os.R_OK):
                raise click.ClickException(f"File '{file_path}' is not readable.")

            message_templates.append(FileMessageTemplate(file=file_path))
            i += 2

        elif args[i] == '--text':
            # Ensure there's a text argument following the option.
            if i + 1 >= len(args):
                raise click.ClickException("Missing argument for --text")
            text_arg = args[i + 1]
            i += 2

            # Check if a mask follows.
            mask_arg = None
            if i < len(args) and args[i] == '--mask':
                if i + 1 >= len(args):
                    raise click.ClickException("Missing argument for --mask")
                mask_arg = args[i + 1]
                i += 2

            message_templates.append(TextMessageTemplate(text=text_arg, mask=mask_arg))

        else:
            # If an unknown option is encountered, raise an error.
            raise click.ClickException(f"Unknown option: {args[i]}")

    return message_templates


def load_image_message(file: Path):
    json_text = file.read_text()
    json_object = json.loads(json_text)
    message = image_message(json_object)
    return message

mask_translation = {
    "r": Colour.red,
    "y": Colour.yellow,
    "g": Colour.green,
    "c": Colour.cyan,
    "b": Colour.blue,
    "m": Colour.magenta,
    "w": Colour.white,
}


def create_text_message(text: str, mask: str):
    invert = [c.isupper() for c in mask]
    translated_mask = [mask_translation.get(c[0].lower(), Colour.white) for c in mask]

    text = [c for c in text]
    return TextMessage(text, translated_mask, invert)

@click.command(context_settings={'allow_extra_args': True, 'ignore_unknown_options': True})
def main():
    """
    This CLI accepts a sequence of message_templates (up to 7), each being either:
      - an image message: --file <filename>
      - a text message: --text <message> [--mask <mask>]

    The order of these options matters.
    """
    message_templates = manual_parsing(sys.argv[1:])

    actual_messages = []
    for message_template in message_templates:
        if isinstance(message_template, FileMessageTemplate):
            actual_messages.append(load_image_message(message_template.file))
        elif isinstance(message_template, TextMessageTemplate):
            actual_messages.append(create_text_message(message_template.text, message_template.mask))

    for message in actual_messages:
        print(message.visualize())

    program = Program(actual_messages)
    device = Device()
    device.program(program)


if __name__ == '__main__':
    main()
