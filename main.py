#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy import logging
import os

from code.load_data import load_config, load_data
from code.experiment_info import experiment_info
from code.triggers import create_eeg_port
from code.screen import create_win
from code.ophthalmic_procedure import ophthalmic_procedure
from code.show_info import show_info, prepare_keys_info

__author__ = 'ociepkam'


def run():
    config = load_config()

    part_id, sex, age, observer_id, keys_matching_version, experiment_order_version, date = experiment_info(config['observer'])

    logging.LogFile(os.path.join('results', 'logs', part_id + '.log'), level=logging.INFO)
    logging.info("Date: {}, ID: {}, Sex: {}, Age: {}, Observer: {}, Keys matching: {}, Experiment order: {}".format(
                  date, part_id, sex, age, observer_id, str(keys_matching_version), str(experiment_order_version)))

    # EEG triggers
    if config['send_EEG_trigg']:
        port_eeg = create_eeg_port()
    else:
        port_eeg = None

    triggers_list = list()
    trigger_no = 0

    # screen
    win, screen_res, frames_per_sec = create_win(screen_color=config['screen_color'])

    # load data
    list_stops = load_data(win=win, folder_name="stop", config=config, screen_res=screen_res)
    list_go = load_data(win=win, folder_name="go", config=config, screen_res=screen_res)
    list_tips = load_data(win=win, folder_name="tip", config=config, screen_res=screen_res)
    # TODO: prepare experiment

    # Keys version
    if keys_matching_version == 2:
        for idx, elem in enumerate(config['keys']):
            if elem['stim'] == '+':
                config['keys'][idx]['stim'] = 'x'
            else:
                config['keys'][idx]['stim'] = '+'
    keys_list = [prepare_keys_info(config['keys'])]

    # Run experiment
    # Ophthalmic procedure
    if config['ophthalmic_procedure']:
        trigger_no, triggers_list = ophthalmic_procedure(win=win, send_eeg_triggers=config['send_EEG_trigg'],
                                                         screen_res=screen_res, frames_per_sec=frames_per_sec,
                                                         port_eeg=port_eeg, trigger_no=trigger_no,
                                                         triggers_list=triggers_list, text_size=config['text_size'],
                                                         text_color=config['text_color'], text_font=config['text_font'])

    # Instruction
    instructions = sorted([f for f in os.listdir('messages') if f.startswith('instruction')])
    for idx, instruction in enumerate(instructions):
        show_info(win=win, file_name=os.path.join('messages', instruction), text_size=config['text_size'],
                  text_color=config['text_color'], text_font=config['text_font'], screen_width=screen_res['width'],
                  replace_list=keys_list[idx])

    # TODO:
    #       Training
    #       Experiment
    #       Save data

    # Experiment end
    show_info(win=win, file_name=os.path.join('messages', 'end.txt'), text_size=config['Text_size'],
              screen_width=screen_res['width'])
    logging.flush()


run()
