import readchar
from .. import utils

@utils.ensure('?25h', '0m')
def confirm(
    prompt: str,
    true: str = 'Yes',
    false: str = 'No',
    default: bool = True,
    hover: int | str = 106
) -> bool:
    '''
    A prompt for confirming an option.

    :param prompt: Prompt message.
    :param true: Confirmation button content.
    :param false: Refute button content.
    
    :return: The confirmation result.
    '''

    result = default
    style = [0, hover]

    # Ensure choices stay on one line
    strip = len(prompt) + 6 # prompt pad + true & false pads
    true = utils.inline(true, buffer = strip + 5) # Min space for false
    false = utils.inline(false, buffer = strip + len(true))
    
    while 1:
        style.sort(reverse = result)
        print(
            f'\x1b[?25l\x1b[0m{prompt} '
            f'\x1b[{style[0]}m {true} '
            f'\x1b[0m\x1b[{style[1]}m {false} \x1b[0m',
            end = '\r'
        )
        
        key = readchar.readkey()

        if key == readchar.key.LEFT and not result: result = True
        if key == readchar.key.RIGHT and result: result = False
        if key == readchar.key.ENTER: break
    
    print()
    return result

# EOF