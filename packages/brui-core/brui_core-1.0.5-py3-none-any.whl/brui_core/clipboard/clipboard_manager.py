import pyperclip
import asyncio

async def wait_for_clipboard_content():
    """
    Wait for the clipboard content to change and return the new content.
    
    :return: The new clipboard content as a string
    """
    initial_clipboard = pyperclip.paste()
    if initial_clipboard != '':
        return initial_clipboard

    while True:
        await asyncio.sleep(0.1)
        new_clipboard = pyperclip.paste()
        if new_clipboard != initial_clipboard:
            pyperclip.copy('')
            return new_clipboard
