import re


def get_screen_size(window):
    return window.winfo_screenwidth(), window.winfo_screenheight()


def center_window(window, width, height):
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
    window.geometry(size)


def correct_subject(subject):
    pattern = r"[\\\n]"
    new_subject = re.sub(pattern, "", subject)
    return new_subject

def replace_minus_as_slash(subject):
    pattern = r"[-]"
    new_subject = re.sub(pattern, "/", subject)
    return new_subject

