import time


class TriggerTypes(object):
    BLINK = 'BLINK'
    GO = 'GO'
    ST = 'ST'
    RE = 'RE'
    TIP = 'TI'


def create_eeg_port():
    try:
        import parallel
        port = parallel.Parallel()
        port.setData(0x00)
        return port
    except:
        raise Exception("Can't connect to EEG")


def prepare_trigger_name(trial, stop_show_start=None):
    name = "*{}*{}".format(trial['go'][1], trial['tip'][1])
    if trial['stop'] is not None:
        name += '*{}*{}'.format(trial['stop'][1], stop_show_start)
    else:
        name += '*-*-*-'
    # for response and acc
    name += '*-*-'
    return name


def prepare_trigger(trigger_no, triggers_list, trigger_type, trigger_name=None):
    trigger_no += 1
    if trigger_no == 9:
        trigger_no = 1
    if trigger_name is not None:
        trigger_type = trigger_type + trigger_name
    triggers_list.append((str(trigger_no), trigger_type))
    return trigger_no, triggers_list


def send_trigger(trigger_no, port_eeg=None, port_nirs=None, send_eeg_triggers=False, send_nirs_triggers=False):
    if send_eeg_triggers:
        try:

            port_eeg.setData(trigger_no)

            time.sleep(0.01)
            port_eeg.setData(0x00)
        except:

            pass
    if send_nirs_triggers:
        try:
            port_nirs.activate_line(trigger_no)
        except:
            pass
