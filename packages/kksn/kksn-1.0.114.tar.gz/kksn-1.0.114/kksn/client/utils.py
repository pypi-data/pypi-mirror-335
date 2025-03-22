# -*- coding: utf-8 -*-
import random
import string
from tkinter import messagebox, Tk


def get_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


def check_type(name='', value=None, value_type=str):
    if value is None:
        return

    if not isinstance(value, value_type):
        raise ValueError(f'{name} must be {value_type.__name__} or None')


def show_error_message(title, message):
    root = Tk()
    root.withdraw()
    messagebox.showerror(title, message, master=root)
