#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy import logging

from code.load_data import load_config
from code.experiment_info import experiment_info
from code.triggers import create_eeg_port
from code.screen import create_win

__author__ = 'ociepkam'


def run():
    config = load_config()

    part_id, sex, age, observer_id, date, keys_matching_version, experiment_order_version = experiment_info(config['observer'])

    logging.LogFile('results/logs/' + part_id + '.log', level=logging.INFO)
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


    logging.flush()


run()
