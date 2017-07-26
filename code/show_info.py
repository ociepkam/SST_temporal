from psychopy import visual, event
import os

from code.load_data import read_text_from_file


def prepare_keys_info(keys_info):
    res = []
    for elem in keys_info:
        res.append(elem['key'])
        res.append(elem['hand'])
        res.append(elem['stim'])
    return res


def show_info(win, file_name, text_size, screen_width, insert='',
              replace_list=None, text_color='black', text_font='Arial'):
    """
    Clear way to show info message into screen.
    :param text_font:
    :param text_color:
    :param replace_list: list with elements to replace {} in text
    :param win:
    :param file_name:
    :param screen_width:
    :param text_size:
    :param insert: extra text for read_text_from_file
    :return:
    """
    hello_msg = read_text_from_file(file_name, insert=insert)
    if replace_list is not None:
        for elem in replace_list:
            try:
                hello_msg = hello_msg.replace("{}", elem, 1)
            except:
                raise TypeError('to less {} in  instruction')
    hello_msg = visual.TextStim(win=win, antialias=True, font=text_font,
                                text=hello_msg, height=text_size,
                                wrapWidth=screen_width, color=text_color,
                                alignHoriz='center', alignVert='center')
    hello_msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space'])
    if key == ['f7']:
        exit(0)
    win.flip()


def break_info(show_answers_correctness, show_response_time, show_stopped_ratio, show_keys_mapping, answers_correctness,
               response_time, stopped_ratio, keys_mapping):
    extra_info = ""
    if show_answers_correctness:
        file_name = os.path.join('messages', 'answers_correctness.txt')
        extra_info += read_text_from_file(file_name=file_name, insert=answers_correctness) + '\n'
    if show_response_time:
        file_name = os.path.join('messages', 'response_time.txt')
        extra_info += read_text_from_file(file_name=file_name, insert=response_time) + '\n'
    if show_stopped_ratio:
        file_name = os.path.join('messages', 'stopped_ratio.txt')
        extra_info += read_text_from_file(file_name=file_name, insert=stopped_ratio) + '\n'
    if show_keys_mapping:
        extra_info += keys_mapping + '\n'

    return extra_info


