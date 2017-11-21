#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy import logging
import os
import copy

from code.load_data import load_config, load_data
from code.experiment_info import experiment_info
from code.triggers import create_eeg_port
from code.screen import create_win
from code.prepare_experiment import create_stops_times_dict, prepare_experiment
from code.ophthalmic_procedure import ophthalmic_procedure
from code.show_info import show_info, prepare_keys_info
from code.show import show
from code.save_data import save_beh, save_triggers

__author__ = 'ociepkam'

folder_stop = os.path.join('stimulus', 'stop')
folder_go = os.path.join('stimulus', 'go')
folder_tip = os.path.join('stimulus', 'tip')
folder_fixation = os.path.join('stimulus', 'fixation_point')


def run():
    config = load_config()

    part_id, sex, age, observer_id, keys_matching_version, experiment_order_version, date = experiment_info(
        config['observer'])

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
    screen_color = list(map(lambda x: (x-128)/128., config['screen_color']))
    print screen_color
    win, screen_res, frames_per_sec = create_win(screen_color=screen_color)

    # load data
    list_stops = load_data(win=win, folder_name=folder_stop, config=config, screen_res=screen_res)
    list_go = load_data(win=win, folder_name=folder_go, config=config, screen_res=screen_res)
    list_tips = load_data(win=win, folder_name=folder_tip, config=config, screen_res=screen_res)
    fixation = load_data(win=win, folder_name=folder_fixation, config=config, screen_res=screen_res)[0]

    # prepare stop tricking for each tip
    stops_times = create_stops_times_dict(list_tips, config['stop_start_wait_time'])
    stops_times_train = copy.copy(stops_times)

    experiment_blocks = config['experiment_blocks_v{}'.format(experiment_order_version)]

    training, experiment = prepare_experiment(training_blocks=config['training_blocks'],
                                              experiment_blocks=experiment_blocks,
                                              list_go=list_go, list_tip=list_tips, list_stops=list_stops,
                                              percent_of_trials_with_stop=config['stop_traials_in_percentage'])

    # Keys version
    if keys_matching_version == 2:
        for idx, elem in enumerate(config['keys']):
            if elem['stim'] == '+':
                config['keys'][idx]['stim'] = 'x'
            else:
                config['keys'][idx]['stim'] = '+'
    keys_info_list = [prepare_keys_info(config['keys'])]
    config['keys_list'] = [elem['key'] for elem in config['keys']]

    # ---------------------- Run experiment ---------------------- #
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
                  replace_list=keys_info_list[idx])

    # Training
    show(config=config, win=win, screen_res=screen_res, frames_per_sec=frames_per_sec, blocks=training,
         stops_times=stops_times_train, background=fixation, trigger_no=trigger_no, triggers_list=list())

    # Experiment
    beh, triggers_list = show(config=config, win=win, screen_res=screen_res, frames_per_sec=frames_per_sec,
                              blocks=experiment, stops_times=stops_times, background=fixation,
                              trigger_no=trigger_no, triggers_list=list(), port_eeg=port_eeg)

    # Save data
    save_beh(data=beh, name=part_id)
    save_triggers(data=triggers_list, name=part_id)

    # Experiment end
    show_info(win=win, file_name=os.path.join('messages', 'end.txt'), text_size=config['text_size'],
              text_color=config['text_color'], screen_width=screen_res['width'])
    logging.flush()


run()
