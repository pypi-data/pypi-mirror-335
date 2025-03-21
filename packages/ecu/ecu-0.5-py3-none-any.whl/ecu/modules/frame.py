import os
import typing
from .. import utils

Style = typing.Literal['SIMPLE', 'DOUBLE', 'ROUNDED'] | str

Borders = dict(
    SIMPLE  = '─│┌┐┘└',
    DOUBLE  = '═║╔╗╝╚',
    ROUNDED = '─│╭╮╯╰'
)

def frame(
    message: str,
    *lines: str,
    border: Style = 'ROUNDED',
    max_width: int = 200,
    color: str = 36,
) -> None:
    '''
    Display a title frame.

    :param message: Main message to show.
    :param lines: Additional lines to display.
    :param border: Border style or custom sequence.
    :param width: Frame width.
    :param color: Main message ANSI style.
    '''

    border = Borders.get(border, border)

    width = min(os.get_terminal_size().columns, max_width) - 2

    print('\x1b[2m' + border[2] + border[0] * width + border[3])
    print(border[1] + f'\x1b[0m\x1b[{color}m' + message.center(width) + '\x1b[0m\x1b[2m' + border[1])

    for line in lines:
        print(border[1] + f'\x1b[0m' + line.center(width) + '\x1b[2m' + border[1])

    print('\x1b[2m' + border[5] + border[0] * width + border[4])

# EOF