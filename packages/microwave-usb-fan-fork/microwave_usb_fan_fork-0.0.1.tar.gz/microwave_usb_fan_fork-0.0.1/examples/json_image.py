from microwave_usb_fan_fork import Colour, Column, Message


def image_message(json_object: list):
    """
    Convert a JSON object to a Message object

    The JSON object is a list of dictionaries, each dictionary
    representing a column of pixels. Each dictionary has two keys:
    "column" and "color". The "column" key is a list of booleans
    representing the pixels in the column. The "color" key is a string
    representing the colour of the column, with the possible values:
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white".

    Example of a valid structure:
    ```python
    valid = [
        {"column": [True, False, True, False, True, False, True, False, True, False, True], "color": "red"},
        {"column": [True, False, True, False, True, False, True, False, True, False, True], "color": "green"},
        {"column": [True, False, True, False, True, False, True, False, True, False, True], "color": "blue"},
    ]
    ```

    :param json_object: The JSON object to convert
    :return: The Message object that you con upload in a program.
    """

    color_translation = {
        "black": Colour.white,
        "red": Colour.red,
        "green": Colour.green,
        "yellow": Colour.yellow,
        "blue": Colour.blue,
        "magenta": Colour.magenta,
        "cyan": Colour.cyan,
        "white": Colour.white,
    }

    columns = [
        Column(
            [True if pixel else False for pixel in i["column"]],
            color_translation[i["color"]],
        )
        for i in json_object
    ]

    return Message(columns)
