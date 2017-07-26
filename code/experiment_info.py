import datetime
from psychopy import gui


# TODO: choosing type of experiment (key matching, blocks order)
def experiment_info(observer):
    """
    okienko dialogowe na podczas uruchomienia procedury
    :param observer: observer_id
    :return: part_id, observer_id, date
    """
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M")

    my_dlg = gui.Dlg(title="SST_temporal")
    my_dlg.addText('Subject info')
    my_dlg.addField('ID:', 'id')
    my_dlg.addField('Age:', 20)
    my_dlg.addField('Sex:', choices=['MALE', "FEMALE"])
    my_dlg.addText('Observer info')
    my_dlg.addField('Observer:', observer)
    my_dlg.addField('Keys matching:', choices=[1, 2])
    my_dlg.addField('Experiment order:', choices=[1, 2])

    my_dlg.show()
    if not my_dlg.OK:
        exit(1)

    #          id               sex             age          observer       keys matching        experiment order
    return my_dlg.data[0], my_dlg.data[2], my_dlg.data[1], my_dlg.data[3], int(my_dlg.data[4]), int(my_dlg.data[5]), date
