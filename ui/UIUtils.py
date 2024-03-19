import re


def get_screen_size(window):
    return window.winfo_screenwidth(), window.winfo_screenheight()


def center_window(window, width, height):
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
    window.geometry(size)


def correct_subject(subject):
    char_list = [subject[j] for j in range(len(subject)) if ord(subject[j]) in range(65536)]
    new_subject = ''

    for j in char_list:
        new_subject = new_subject + j

    pattern = r"[\\\n]"
    new_subject = re.sub(pattern, "", new_subject)
    return new_subject

def replace_minus_as_slash(subject):
    pattern = r"[-]"
    new_subject = re.sub(pattern, "/", subject)
    return new_subject

