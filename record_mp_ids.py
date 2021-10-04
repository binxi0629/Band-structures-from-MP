import os,re


def record_mp_ids(data_dir="data/"):

    mp_id_list=[]
    for dirs, subdirs, files in os.walk(data_dir):
        for file in files:
            tmp = re.split('\.', file)[0]
            mp_id = int(re.split('_', tmp)[-1])
            mp_id_list.append(mp_id)

    return mp_id_list

