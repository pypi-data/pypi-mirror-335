import os
import typing

def ensure(*codes: str) -> typing.ContextManager:
    '''
    Ensures to cleanup after a function exit.
    '''

    cleanup = ''.join('\x1b[' + code for code in codes)

    def decorator(func: typing.Callable):
        def wrapper(*args, **kwargs):
            try:
                print('\x1b7', end = '')
                return func(*args, **kwargs)
            
            finally:
                # Cleanup
                print('\x1b8\x1b[J' + cleanup, end = '')
        
        return wrapper
    return decorator

def inline(value: str, buffer: int = 0) -> str:
    '''
    ...
    '''

    raw = str(value)
    size = os.get_terminal_size().columns - buffer

    if len(raw) > size:
        raw = raw[:size - 1] + '…'
    
    return raw

# EOF