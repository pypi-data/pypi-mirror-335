import typing
import readchar
from .. import utils

__max = max

PINS = ('\x1b[2m-\x1b[0m', '+')

@utils.ensure('?25h', '0m', '=7h')
def select(
    prompt: str,
    choices: typing.Iterable,
    max: int | None = 1,
    size: int | None = 10,
    hover: int | str = 36
) -> list | typing.Any:
    '''
    A prompt for selecting item(s) in a list.

    Bindings:
        - up/down: Move cursor
        - space: toggle line selection
        - home/end: Go to start/end of list
        - a: Toggle all items
        - r: Reset selection
        - s: Start range selection
        - shift+s: End range selection
        - enter: Confirm selection
    
    :param prompt: Prompt to display before the menu.
    :param choices: Iterable of choices.
    :param max: Max amount of choices. Set to null for infinite.
    :param size: Display length of the menu. Set to None to display entire menu.
    :param hover: ANSI code to apply when hovering.

    :return: List of choices, or the choice directly if `max` is set to 1.
    '''

    row = 0
    scroll = 0
    sel: list[int] = []
    choices = list(choices) # Convenient for passing iterator directly
    size = size if size else len(choices)
    range_start = 0
    message = ''

    print(prompt)

    def toggle(line: int) -> None:
        # Toggles a line

        if line in sel: sel.remove(line)
        elif not max or len(sel) < max: sel.append(line)
    
    while 1:
        for choice_index, choice in enumerate(choices[scroll:scroll + size]):
            i = scroll + choice_index
            print('\x1b[?25l\x1b[0m\x1b[2K'
                  f'{PINS[i in sel]} \x1b[{hover if i == row else 0}m'
                  f'{utils.inline(choice, buffer = 2)}\x1b[0m'
            )
        
        # Show bottom text
        raw_message = utils.inline(f'#{row} | {len(sel)}/{len(choices)} selected' + message)
        print(f'\x1b[2m\x1b[2K{raw_message}\x1b[0m\x1b[{min(size, len(choices))}A\x1b[0G', end = '', flush = True)
        key = readchar.readkey()

        # Reset message
        message = ''

        # Move cursor up
        if key == readchar.key.UP:
            if row > 0: row -= 1
            if row < scroll: scroll -= 1

        # Move cursor down
        if key == readchar.key.DOWN:
            if row < len(choices) - 1: row += 1
            if row >= scroll + size: scroll += 1
        
        # Go to top
        if key == readchar.key.HOME:
            row = scroll = 0
        
        # Go to bottom
        if key == readchar.key.END:
            row = len(choices) - 1
            scroll = __max(0, len(choices) - size)
        
        # Toggle line
        if key == readchar.key.SPACE and max != 1:
            toggle(row)
            last_toggle = row
        
        # Toggle all lines
        if key in 'aA':
            for i in range(len(choices)):
                toggle(i)
            message = ' | Toggled all lines'
        
        # Set range start
        if key == 's':
            range_start = row
            message = f' | Started range at row {row}'
        
        # Select range
        if key == 'S':
            start, end = sorted((range_start, row))
            for i in range(start - 1, end):
                toggle(i + 1)
            message = f' | Applied selection {start}-{end}'
        
        # Reset selection
        if key in 'rR':
            sel = []
            range_start = 0
            message = ' | Selection reset'
        
        # Confirm or direct select
        if key == readchar.key.ENTER:
            if not sel: sel = [row]
            break
    
    sel.sort()
    result = [choices[i] for i in sel]
    return result if max != 1 else result[0]

# EOF