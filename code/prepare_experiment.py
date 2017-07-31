import random
import os


def prepare_go(list_go, number_of_trials):
    number_of_go_types = len(list_go)
    go_table = range(number_of_go_types) * (number_of_trials / number_of_go_types)

    missing_trials = number_of_trials % number_of_go_types
    rest_trials = range(number_of_go_types)
    random.shuffle(rest_trials)

    go_table += rest_trials[:missing_trials]
    random.shuffle(go_table)

    go_table = [list_go[x] for x in go_table]

    return go_table


def prepare_stops(stops, number_of_trials, percent_of_trials_with_stop=25):
    number_of_stop_types = len(stops)
    number_of_trials_with_stop = int(round(number_of_trials * percent_of_trials_with_stop / 100.))
    stop_table = range(number_of_stop_types) * (number_of_trials_with_stop / number_of_stop_types)

    missing_trials = number_of_trials_with_stop % number_of_stop_types
    rest_trials = range(number_of_stop_types)
    random.shuffle(rest_trials)

    stop_table += rest_trials[:missing_trials]

    # create trials without stops
    trials_without_stop = [None] * (number_of_trials - 2 * len(stop_table))
    stop_table += trials_without_stop
    random.shuffle(stop_table)

    # removing trials with stops with are one by one
    new_stop_table = []
    for trial in stop_table:
        new_stop_table.append(trial)
        if trial >= 0:
            new_stop_table.append(None)

    new_stop_table = [stops[x] if x is not None else None for x in new_stop_table]

    return new_stop_table


def block_part_creator(go_table, stop_table, tip):
    assert len(stop_table) == len(go_table), "len(stop_table) != len(arrows_table)"
    block_part = [{'go': go, 'stop': stop, 'tip': tip} for go, stop in zip(go_table, stop_table)]
    random.shuffle(block_part)
    return block_part


def blocks_creator(blocks, breaks):
    assert len(blocks) == len(breaks), "len(blocks) != len(breaks)"
    blocks = [{'trials': block, 'text_after_block': text} for block, text in zip(blocks, breaks)]
    return blocks


def prepare_trials(blocks, list_go, list_tip, list_stops, percent_of_trials_with_stop, breaks_name):
    trials = []
    if blocks:
        for block in blocks:
            training_block = []
            for block_part in block:
                for trials_type_key, trials_type_value in block_part.iteritems():
                    block_part_go_list = prepare_go(list_go=list_go, number_of_trials=trials_type_value)
                    block_part_stop_list = prepare_stops(stops=list_stops, number_of_trials=trials_type_value,
                                                         percent_of_trials_with_stop=percent_of_trials_with_stop)
                    block_part_tip = [elem for elem in list_tip if elem[1] == trials_type_key][0]
                    training_block_part = block_part_creator(block_part_go_list, block_part_stop_list, block_part_tip)
                    training_block.append(training_block_part)
            trials.append(training_block)
        breaks = [os.path.join('messages', '{}_{}.txt'.format(breaks_name, idx + 1)) for idx in range(len(trials))]
        return blocks_creator(trials, breaks)
    else:
        return []


def prepare_experiment(training_blocks, experiment_blocks, list_go, list_tip, list_stops, percent_of_trials_with_stop):
    assert percent_of_trials_with_stop <= 50, "procent stopow nie moze byc wiekszy od 50"

    training = prepare_trials(training_blocks, list_go, list_tip, list_stops,
                              percent_of_trials_with_stop, 'training_break')

    experiment = prepare_trials(experiment_blocks, list_go, list_tip, list_stops,
                                percent_of_trials_with_stop, 'experiment_break')
    return training, experiment


def create_stops_times_dict(stops, start_wait_to_stop):
    stops_times = dict()
    for stop in stops:
        stops_times[stop[1]] = start_wait_to_stop
    return stops_times
