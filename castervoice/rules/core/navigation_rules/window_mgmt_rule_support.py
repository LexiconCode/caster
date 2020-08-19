# All credit goes to caspark
# This is adapted from caspark's grammar at https://gist.github.com/caspark/9c2c5e2853a14b6e28e9aa4f121164a6

from __future__ import print_function

import re
import time
import datetime

from dragonfly import Window, DictList

import six


open_windows_dictlist = DictList("open_windows")

WORD_SPLITTER = re.compile('[^a-zA-Z0-9]+')


def lower_if_not_abbreviation(s):
    if len(s) <= 4 and s.upper() == s:
        return s
    else:
        return s.lower()


def find_window(window_matcher_func, timeout_ms=3000):
    """Returns a dragonfly Window matching the given matcher function, or raises an error otherwise"""
    steps = timeout_ms / 100
    for i in range(steps):
        for win in Window.get_all_windows():
            if window_matcher_func(win):
                return win
        time.sleep(0.1)
    raise ValueError(
        "no matching window found within {} ms".format(timeout_ms))


def refresh_open_windows_dictlist():
    window_options = {}
    for window in (x for x in Window.get_all_windows() if
                   x.is_valid and
                   x.is_enabled and
                   x.is_visible and
                   not x.executable.startswith("C:\\Windows") and
                   x.classname != "DgnResultsBoxWindow"):
        for word in {lower_if_not_abbreviation(word)
                     for word
                     in WORD_SPLITTER.split(window.title)
                     if len(word)}:
            if word in window_options:
                window_options[word] += [window]
            else:
                window_options[word] = [window]

    window_options = {k: v for k,
                      v in six.iteritems(window_options) if v is not None}
    open_windows_dictlist.set(window_options)


def debug_window_switching():
    options = open_windows_dictlist.copy()
    print("*** Windows known:\n",
          "\n".join(sorted({w.title for list_of_windows in six.itervalues(options) for w in list_of_windows})))

    print("*** Single word switching options:\n", "\n".join(
        "{}: '{}'".format(
            k.ljust(20), "', '".join(window.title for window in options[k])
        ) for k in sorted(six.iterkeys(options)) if len(options[k]) == 1))
    print("*** Ambiguous switching options:\n", "\n".join(
        "{}: '{}'".format(
            k.ljust(20), "', '".join(window.title for window in options[k])
        ) for k in sorted(six.iterkeys(options)) if len(options[k]) > 1))


def switch_window(windows):
    matched_window_handles = {w.handle: w for w in windows[0]}
    for window_options in windows[1:]:
        matched_window_handles = {
            w.handle: w for w in window_options if w.handle in matched_window_handles}

    matched_windows = matched_window_handles.values()
    if len(matched_windows) == 1:
        window = matched_windows[0]
        print("Switcher: switching window to", window.title)
        window.set_foreground()
    else:
        try:
            natlink_window = find_window(
                lambda w: "Messages from Python Macros" in w.title, timeout_ms=100)
            if natlink_window.is_minimized:
                natlink_window.restore()
            else:
                natlink_window.set_foreground()
        except ValueError:
            # window didn't exist, it'll be created when we write some output
            pass

        print("Ambiguous switch command:\n", "\n".join(
            "'{}' from {} (handle: {})".format(w.title, w.executable, w.handle) for w in matched_windows))