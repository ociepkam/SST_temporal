from psychopy import visual, event, core
import time
import random
import pygame
import pyglet
import platform

from code.show_info import show_info, break_info  # , prepare_buttons_info
from code.check_exit import check_exit
from code.triggers import prepare_trigger, TriggerTypes, send_trigger, prepare_trigger_name

SYSTEM = None
PLAYER = None

PORT_EEG = None
PORT_NIRS = None
TRIGGERS_LIST = list()
TRIGGER_NO = 0


def draw_tip(win, tip, show_time):
    tip.setAutoDraw(True)
    win.flip()
    time.sleep(show_time)
    tip.setAutoDraw(False)
    check_exit()
    win.flip()


def start_stimulus(win, stimulus, send_eeg_triggers, send_nirs_triggers):
    global TRIGGER_NO, SYSTEM, PLAYER

    if stimulus[0] == 'image':
        stimulus[2].setAutoDraw(True)
        win.flip()
        send_trigger(port_eeg=PORT_EEG, port_nirs=PORT_NIRS, trigger_no=TRIGGER_NO,
                     send_eeg_triggers=send_eeg_triggers,
                     send_nirs_triggers=send_nirs_triggers)

    elif stimulus[0] == 'text':
        stimulus[2].setAutoDraw(True)
        win.flip()
        send_trigger(port_eeg=PORT_EEG, port_nirs=PORT_NIRS, trigger_no=TRIGGER_NO,
                     send_eeg_triggers=send_eeg_triggers,
                     send_nirs_triggers=send_nirs_triggers)

    elif stimulus[0] == 'sound':
        if 'Linux' in SYSTEM:
            pygame.init()
            pygame.mixer.music.load(stimulus[2])
            win.flip()
            pygame.mixer.music.play()
        elif 'Windows' in SYSTEM:
            sound = pyglet.media.load(stimulus[2])
            PLAYER = pyglet.media.Player()
            PLAYER.queue(sound)
            win.flip()
            PLAYER.play()

        send_trigger(port_eeg=PORT_EEG, port_nirs=PORT_NIRS, trigger_no=TRIGGER_NO,
                     send_eeg_triggers=send_eeg_triggers,
                     send_nirs_triggers=send_nirs_triggers)

    else:
        raise Exception("Problems with start stimulus " + stimulus)


def stop_stimulus(stimulus):
    global SYSTEM, PLAYER
    if stimulus[0] == 'image':
        stimulus[2].setAutoDraw(False)

    elif stimulus[0] == 'text':
        stimulus[2].setAutoDraw(False)

    elif stimulus[0] == 'sound':
        if 'Linux' in SYSTEM:
            pygame.mixer.music.stop()
            pygame.quit()
        elif 'Windows' in SYSTEM:
            PLAYER.pause()
            del PLAYER
    else:
        raise Exception("Problems with stop stimulus " + stimulus)


def run_trial(win, resp_clock, trial, resp_time, go_show_time, stop_show_end, stop_show_start, config,
              real_stop_show_start):
    global PORT_EEG, TRIGGER_NO, TRIGGERS_LIST

    reaction_time = None
    response = None
    # TODO: triggers
    trigger_name = ''  # prepare_trigger_name(trial=trial, stop_show_start=real_stop_show_start)
    TRIGGER_NO, TRIGGERS_LIST = prepare_trigger(trigger_type=TriggerTypes.GO, trigger_no=TRIGGER_NO,
                                                triggers_list=TRIGGERS_LIST, trigger_name=trigger_name)
    start_stimulus(win=win, stimulus=trial['go'], send_eeg_triggers=config['send_EEG_trigg'],
                   send_nirs_triggers=config['send_Nirs_trigg'])
    check_exit()
    go_on = True
    stop_on = None
    event.clearEvents()
    win.callOnFlip(resp_clock.reset)
    win.flip()

    while resp_clock.getTime() < resp_time:
        change = False
        if go_on is True and resp_clock.getTime() > go_show_time:
            stop_stimulus(stimulus=trial['go'])
            go_on = False
            change = True
        if trial['stop'] is not None:
            if stop_on is None and resp_clock.getTime() > stop_show_start:
                TRIGGER_NO, TRIGGERS_LIST = prepare_trigger(trigger_type=TriggerTypes.ST, trigger_no=TRIGGER_NO,
                                                            triggers_list=TRIGGERS_LIST, trigger_name=trigger_name)
                start_stimulus(win=win, stimulus=trial['stop'], send_eeg_triggers=config['send_EEG_trigg'],
                               send_nirs_triggers=config['send_Nirs_trigg'])
                stop_on = True
                change = True
            if stop_on is True and resp_clock.getTime() > stop_show_end:
                stop_stimulus(stimulus=trial['stop'])
                stop_on = False
                change = True

        key = event.getKeys(keyList=config['keys_list'])
        if key:
            reaction_time = resp_clock.getTime()
            TRIGGER_NO, TRIGGERS_LIST = prepare_trigger(trigger_type=TriggerTypes.RE, trigger_no=TRIGGER_NO,
                                                        triggers_list=TRIGGERS_LIST, trigger_name=trigger_name)
            if config['send_EEG_trigg']:
                send_trigger(port_eeg=PORT_EEG, port_nirs=PORT_NIRS, trigger_no=TRIGGER_NO,
                             send_eeg_triggers=config['send_EEG_trigg'],
                             send_nirs_triggers=config['send_Nirs_trigg'])
            response = key[0]
            break
        check_exit()
        if change is False:
            win.flip()

    if go_on is True:
        stop_stimulus(stimulus=trial['go'])
    if stop_on is True:
        stop_stimulus(stimulus=trial['stop'])

    # Add response to all trial triggers
    if response is not None:
        TRIGGERS_LIST[-1] = (TRIGGERS_LIST[-1][0], TRIGGERS_LIST[-1][1][:-1] + response)
        TRIGGERS_LIST[-2] = (TRIGGERS_LIST[-2][0], TRIGGERS_LIST[-2][1][:-1] + response)
        if TRIGGERS_LIST[-2][1].startswith('ST'):
            TRIGGERS_LIST[-3] = (TRIGGERS_LIST[-3][0], TRIGGERS_LIST[-3][1][:-1] + response)

    return reaction_time, response


def update_stops_times(trial, config, response, stops_times):
    if trial['stop'] is not None:
        wait_time_index = config['stop_possible_wait_times'].index(stops_times[trial['tip'][1]])
        if response is None:
            if wait_time_index != len(config['stop_possible_wait_times']) - 1:
                stops_times[trial['tip'][1]] = config['stop_possible_wait_times'][wait_time_index + 1]
        else:
            if wait_time_index != 0:
                stops_times[trial['tip'][1]] = config['stop_possible_wait_times'][wait_time_index - 1]
    return stops_times


def show(config, win, screen_res, frames_per_sec, blocks, stops_times, trigger_no, triggers_list, background,
         port_eeg=None, port_nirs=None):
    global PORT_EEG, PORT_NIRS, TRIGGERS_LIST, TRIGGER_NO, SYSTEM
    SYSTEM = platform.system()

    PORT_EEG = port_eeg
    PORT_NIRS = port_nirs
    TRIGGERS_LIST = triggers_list
    TRIGGER_NO = trigger_no

    # one_frame_time = 1.0 / frames_per_sec

    go_show_time = config['show_time_GO']  # - one_frame_time
    resp_time = config['response_time']  # - one_frame_time

    data = list()
    trial_number = 1
    resp_clock = core.Clock()

    for block in blocks:
        all_reactions_times = 0.
        no_reactions = 0.
        answers_correctness = 0.
        stopped_trials = 0.
        not_stopped_trials = 0.
        for block_part in block['trials']:
            for trial in block_part:
                if trial['stop'] is not None:
                    real_stop_show_start = stops_times[trial['tip'][1]]
                    stop_show_start = real_stop_show_start  # - one_frame_time
                    stop_show_end = stop_show_start + config['show_time_ST']
                else:
                    real_stop_show_start = None
                    stop_show_start = None
                    stop_show_end = None

                # draw tip
                draw_tip(win=win, tip=trial['tip'][2], show_time=config['show_time_tip'])
                check_exit()

                # draw background
                draw_tip(win=win, tip=background[2], show_time=config['show_time_{}'.format(trial['tip'][1])])
                check_exit()

                # go, stop and resp
                reaction_time, response = run_trial(win=win, resp_clock=resp_clock, trial=trial, resp_time=resp_time,
                                                    go_show_time=go_show_time, stop_show_end=stop_show_end,
                                                    stop_show_start=stop_show_start, config=config,
                                                    real_stop_show_start=real_stop_show_start)

                # rest
                check_exit()
                rest_time = random.uniform(config['show_time_break'][0], config['show_time_break'][1])
                draw_tip(win=win, tip=background[2], show_time=rest_time)
                check_exit()

                # add data

                true_RE = [elem['key'] for elem in config['keys'] if elem['stim'] == trial['go'][1]][0]

                if trial['stop'] is not None:
                    data.append({'Nr': trial_number,
                                 'GO_type': trial['go'][0], 'GO_name': trial['go'][1],
                                 'RE_key': response, 'RE_time': reaction_time, 'RE_true': true_RE,
                                 'ST_type': trial['stop'][0], 'ST_name': trial['stop'][1],
                                 'ST_wait_time': stops_times[trial['tip'][1]]})
                else:
                    data.append({'Nr': trial_number,
                                 'GO_type': trial['go'][0], 'GO_name': trial['go'][1],
                                 'RE_key': response, 'RE_true': true_RE, 'RE_time': reaction_time,
                                 'ST_type': None, 'ST_name': None, 'ST_wait_time': None})
                trial_number += 1

                # break info
                if reaction_time is not None:
                    all_reactions_times += reaction_time
                    if response == true_RE:
                        answers_correctness += 1
                else:
                    if trial['stop'] is not None:
                        no_reactions += 1
                    else:
                        all_reactions_times += config['response_time']

                if trial['stop'] is not None:
                    if reaction_time is not None:
                        not_stopped_trials += 1
                    else:
                        stopped_trials += 1

                # update stops_times
                stops_times = update_stops_times(trial=trial, config=config, response=response, stops_times=stops_times)

        # break info

        try:
            all_reactions_times /= (len(block['trials']) - no_reactions)
            all_reactions_times = round(all_reactions_times, 2)
            answers_correctness /= (len(block['trials']) - no_reactions)
            answers_correctness = round(100 * answers_correctness, 2)
        except:
            all_reactions_times = 'No answers!'
            answers_correctness = 'No answers!'
        try:
            stopped_ratio = stopped_trials / (not_stopped_trials + stopped_trials)
            stopped_ratio = round(100 * stopped_ratio, 2)
        except:
            stopped_ratio = 'No stops!'

        break_extra_info = break_info(show_answers_correctness=config['break_show_answers_correctness'],
                                      show_response_time=config['break_show_response_time'],
                                      show_stopped_ratio=config['break_show_stopped_ratio'],
                                      show_keys_mapping=False,
                                      answers_correctness=str(answers_correctness) + '%',
                                      response_time=str(all_reactions_times) + 's',
                                      stopped_ratio=str(stopped_ratio) + '%',
                                      keys_mapping=None)

        show_info(win=win, file_name=block['text_after_block'], text_size=config['text_size'],
                  text_color=config['text_color'], screen_width=screen_res['width'], insert=break_extra_info)

    return data, TRIGGERS_LIST
