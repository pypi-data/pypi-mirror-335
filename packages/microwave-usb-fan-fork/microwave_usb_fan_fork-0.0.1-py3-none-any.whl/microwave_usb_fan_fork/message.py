import bisect
import importlib.resources as pkg_resources
from os.path import dirname, join
from microwave_usb_fan_fork import fonts

from PIL import Image, ImageDraw, ImageFont

from .protocol import (
    Colour,
    Column,
    Message,
    MessageStyle,
    OpenTransition,
    CloseTransition,
)


class TextMessage(Message):
    def __init__(
        self,
        texts: str | list[str],
        colors: Colour | list[Colour] = Colour.white,
        inverts: bool | list[bool] = False,
        message_style: MessageStyle = MessageStyle.Anticlockwise,
        open_transition: OpenTransition = OpenTransition.LeftRight,
        close_transition: CloseTransition = CloseTransition.RightLeft,
    ):
        if isinstance(texts, str):
            texts = [texts]
        if isinstance(colors, Colour):
            colors = [colors] * len(texts)
        if isinstance(inverts, bool):
            inverts = [inverts] * len(texts)


        # Open the font, create a blank image and an ImageDraw object
        fnt = ImageFont.truetype(
            pkg_resources.files(fonts).joinpath("Hack-Regular.ttf")
        )
        img = Image.new("RGB", (Message.MAX_COLUMNS, Column.PIXELS))
        draw = ImageDraw.Draw(img)

        color_map = []
        position_map = []
        pos = 0
        for text, color, invert in zip(texts, colors, inverts):
            # Write the text into the image
            draw.text((pos, -1), text, font=fnt)
            x1, y1, x2, y2 = draw.textbbox((pos, -1), text, font=fnt)
            pos = x2
            color_map.append((color, invert))
            position_map.append(pos)

        # Transpose the image
        img = img.transpose(Image.TRANSPOSE)

        # Convert the image into one channel
        img_data = []
        for idx, pixel in enumerate(img.convert("L").getdata(0)):
            insert_point = bisect.bisect_right(position_map, idx // Column.PIXELS)
            if insert_point >= len(position_map):
                insert_point = len(position_map) - 1
            _, invert = color_map[insert_point]
            img_data.append((pixel >= 128) ^ invert)


        # Convert the image into its columns
        columns = []
        for i in range(0, len(img_data), Column.PIXELS):
            pixel_data = img_data[i : i + Column.PIXELS]
            insert_point = bisect.bisect_right(position_map, i // Column.PIXELS)
            if insert_point >= len(position_map):
                insert_point = len(position_map) - 1
            color, invert = color_map[insert_point]
            columns.append(Column(pixel_data, color))

        super().__init__(columns, message_style, open_transition, close_transition)
