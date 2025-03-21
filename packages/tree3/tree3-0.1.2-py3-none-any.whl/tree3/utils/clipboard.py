import platform
import subprocess


def copy_to_clipboard(text):
    """
    Copy text to clipboard in a cross-platform way.

    Args:
        text (str): Text to copy to clipboard

    Raises:
        Exception: If clipboard operation fails
    """
    system = platform.system()

    try:
        if system == 'Windows':
            # Windows approach
            import ctypes
            from ctypes import wintypes

            # Windows constants
            CF_UNICODETEXT = 13
            GMEM_MOVEABLE = 0x0002

            # Load user32 and kernel32 DLLs
            user32 = ctypes.WinDLL('user32')
            kernel32 = ctypes.WinDLL('kernel32')

            # Set proper argument and return types to prevent overflow errors
            user32.OpenClipboard.argtypes = [wintypes.HWND]
            user32.OpenClipboard.restype = wintypes.BOOL
            user32.EmptyClipboard.restype = wintypes.BOOL
            user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
            user32.SetClipboardData.restype = wintypes.HANDLE
            user32.CloseClipboard.restype = wintypes.BOOL

            kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
            kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
            kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
            kernel32.GlobalLock.restype = wintypes.LPVOID
            kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
            kernel32.GlobalUnlock.restype = wintypes.BOOL

            # Convert text to UTF-16 bytes (with null terminator)
            text_bytes = (text + '\0').encode('utf-16le')
            buffer_size = len(text_bytes)

            # Allocate global memory for clipboard data
            h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, buffer_size)
            if not h_mem:
                raise Exception("Could not allocate memory for clipboard")

            # Lock the memory to get a pointer
            p_mem = kernel32.GlobalLock(h_mem)
            if not p_mem:
                kernel32.GlobalFree(h_mem)
                raise Exception("Could not lock memory for clipboard")

            # Copy data to allocated memory
            ctypes.memmove(p_mem, text_bytes, buffer_size)
            kernel32.GlobalUnlock(h_mem)

            # Transfer data to clipboard
            if not user32.OpenClipboard(None):
                kernel32.GlobalFree(h_mem)
                raise Exception("Could not open clipboard")

            user32.EmptyClipboard()
            if not user32.SetClipboardData(CF_UNICODETEXT, h_mem):
                user32.CloseClipboard()
                kernel32.GlobalFree(h_mem)
                raise Exception("Could not set clipboard data")

            user32.CloseClipboard()

        elif system == 'Darwin':
            # macOS
            process = subprocess.Popen(
                ['pbcopy'],
                stdin=subprocess.PIPE,
                close_fds=True
            )
            process.communicate(text.encode('utf-8'))

            if process.returncode != 0 and process.returncode is not None:
                raise Exception(
                    f"pbcopy failed with return code {process.returncode}")

        else:
            # Linux and others (requires xclip or xsel)
            try:
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard'],
                    stdin=subprocess.PIPE,
                    close_fds=True
                )
                process.communicate(text.encode('utf-8'))

                if process.returncode != 0 and process.returncode is not None:
                    raise Exception(
                        f"xclip failed with return code {process.returncode}")

            except FileNotFoundError:
                try:
                    process = subprocess.Popen(
                        ['xsel', '--clipboard', '--input'],
                        stdin=subprocess.PIPE,
                        close_fds=True
                    )
                    process.communicate(text.encode('utf-8'))

                    if (process.returncode != 0
                            and process.returncode is not None):
                        raise Exception("xsel failed with return code "
                                        f"{process.returncode}")

                except FileNotFoundError:
                    raise Exception(
                        "Neither xclip nor xsel is available. "
                        "Please install one of them.")
    except Exception as e:
        raise Exception(f"Failed to copy to clipboard: {e}")
