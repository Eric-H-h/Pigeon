from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
import struct
import time


CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
_EXCLUDE_FORMAT = "ExcludeClipboardContentFromMonitorProcessing"
_HISTORY_FORMAT = "CanIncludeInClipboardHistory"
_CLOUD_FORMAT = "CanUploadToCloudClipboard"


class ClipboardError(RuntimeError):
    """Raised when sensitive clipboard data cannot be written safely."""


def copy_sensitive(text: str) -> None:
    """Copy text while asking Windows to exclude it from history and cloud sync."""
    if os.name != "nt":
        raise ClipboardError("Sensitive clipboard support is available only on Windows.")
    if not isinstance(text, str) or not text:
        raise ClipboardError("Clipboard text must be a non-empty string.")

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _configure_win32_functions(user32, kernel32)

    formats = (
        (user32.RegisterClipboardFormatW(_EXCLUDE_FORMAT), struct.pack("<I", 1)),
        (user32.RegisterClipboardFormatW(_HISTORY_FORMAT), struct.pack("<I", 0)),
        (user32.RegisterClipboardFormatW(_CLOUD_FORMAT), struct.pack("<I", 0)),
        (CF_UNICODETEXT, text.encode("utf-16-le") + b"\x00\x00"),
    )
    if any(format_id == 0 for format_id, _ in formats):
        raise _last_error("RegisterClipboardFormatW")

    for attempt in range(10):
        if user32.OpenClipboard(None):
            break
        if attempt == 9:
            raise _last_error("OpenClipboard")
        time.sleep(0.05)

    owned_handles: set[int] = set()
    try:
        if not user32.EmptyClipboard():
            raise _last_error("EmptyClipboard")

        for format_id, payload in formats:
            handle = _allocate_global_bytes(kernel32, payload)
            owned_handles.add(handle)
            if not user32.SetClipboardData(format_id, handle):
                raise _last_error("SetClipboardData")
            owned_handles.remove(handle)
    finally:
        for handle in owned_handles:
            kernel32.GlobalFree(handle)
        user32.CloseClipboard()


def _configure_win32_functions(user32: object, kernel32: object) -> None:
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = wintypes.BOOL
    user32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]
    user32.RegisterClipboardFormatW.restype = wintypes.UINT

    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL
    kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalFree.restype = wintypes.HGLOBAL


def _allocate_global_bytes(kernel32: object, payload: bytes) -> int:
    handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(payload))
    if not handle:
        raise _last_error("GlobalAlloc")
    pointer = kernel32.GlobalLock(handle)
    if not pointer:
        kernel32.GlobalFree(handle)
        raise _last_error("GlobalLock")
    try:
        ctypes.memmove(pointer, payload, len(payload))
    finally:
        kernel32.GlobalUnlock(handle)
    return int(handle)


def _last_error(operation: str) -> ClipboardError:
    return ClipboardError(f"{operation} failed with Windows error {ctypes.get_last_error()}.")
