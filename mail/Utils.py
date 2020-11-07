import re


def validate_file_name(file_name):
    pattern = r"[\/\\\:\*\?\"\<\>\|]"
    new_file_name = re.sub(pattern, "_", file_name)
    return new_file_name


def time_tuple_to_number(tuple_time, pure_number=True):
    number_time = str(tuple_time[0])

    if not pure_number:
        number_time = number_time + '/'

    for index in range(1, 6):
        if tuple_time[index] < 10:
            number_time = number_time + '0' + str(tuple_time[index])
        else:
            number_time = number_time + str(tuple_time[index])

        if not pure_number and index == 1:
            number_time = number_time + '/'
        elif not pure_number and index == 2:
            number_time = number_time + ' '
        elif not pure_number and (index == 3 or index == 4):
            number_time = number_time + ':'

    return number_time


def verify_email_address(input_str):
    """
    Helper function to verify the email address

    return: tuple (server, address). Eg. ('imap.example.com', 'jdoe@example.com')
    """
    server_str = None
    pattern = '/^([\w-_]+(?:\.[\w-_]+)*)@((?:[a-z0-9]+(?:-[a-zA-Z0-9]+)*)+\.[a-z]{2,6})$/i'

    if type(input_str) is str:
        re.match(pattern, input_str)
        server_str = 'imap.' + input_str.split('@')[1]

    return server_str


def get_server_from_email_address(input_str):
    str_server = None

    if input_str is not None and type(input_str) is str:
        tmp_str_arrays = input_str.split('@')

        if len(tmp_str_arrays) == 2 and tmp_str_arrays[1] != '':
            str_server = 'imap.' + input_str.split('@')[1]

    return str_server
