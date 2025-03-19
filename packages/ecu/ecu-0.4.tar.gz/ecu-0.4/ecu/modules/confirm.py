import readchar
from .. import utils

@utils.ensure('?25h', '0m')
def confirm(
    prompt: str,
    confirm: str = 'Yes',
    refute: str = 'No',
    default: bool = True,
    hover: int | str = 106
) -> bool:
    '''
    A prompt for confirming an option.

    :param prompt: Prompt message.
    :param confirm: Confirmation button content.
    :param refute: Refute button content.
    
    :return: The confirmation result.
    '''

    result = default
    style = [0, hover]
    
    while 1:
        style.sort(reverse = result)
        print(
            f'\x1b[?25l\x1b[0m{prompt} '
            f'\x1b[{style[0]}m {confirm} '
            f'\x1b[0m\x1b[{style[1]}m {refute} \x1b[0m',
            end = '\r'
        )

        key = readchar.readkey()

        if key == readchar.key.LEFT and not result: result = True
        if key == readchar.key.RIGHT and result: result = False
        if key == readchar.key.ENTER: break
    
    print()
    return result

# EOF