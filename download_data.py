import pymatgen
from pymatgen.ext.matproj import MPRester
import numpy as np
from pymatgen.electronic_structure.core import Spin
import json
import os
import re
from _ctypes import PyObj_FromPtr
import pandas as pd

# from utils.progress_bar import ProgressBar


class NoIndent(object):
    """ Wrapper class to override default JSONEncoder formatting of Python lists and tuples
        which are converted into JSON arrays."""
    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        return repr(self.obj)


def two_d_format(arr):
    return [NoIndent(i) for i in arr]


class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'  # to convert NoIndent object id's in a unique string pattern
    obj_id_pattern = re.compile(FORMAT_SPEC.format(r'(\d+)'))  # regex: r'@@(\d+)@@'

    @staticmethod
    def di(obj_id):
        """ Inverse of built-in id() function.
            see https://stackoverflow.com/a/15012814/355230
        """
        return PyObj_FromPtr(obj_id)

    def default(self, obj):
        if isinstance(obj, NoIndent):
            return self.FORMAT_SPEC.format(id(obj))
        else:
            return super(MyEncoder, self).default(obj)

    def iterencode(self, obj, **kwargs):
        for encoded in super(MyEncoder, self).iterencode(obj, **kwargs):
            # check for list and tuple value that was turned into NoIndent instance
            match = self.obj_id_pattern.search(encoded)
            if match:
                id = int(match.group(1))  # turn it into list object for formatting
                list_obj = list(self.di(int(id)).obj)
                encoded = encoded.replace(
                            '"{}"'.format(self.FORMAT_SPEC.format(id)), repr(list_obj))
            yield encoded


# configs here
m = MPRester("xxxxxxxxxxxx")
verbose = False
n_thread = 28*4
# n_thread = 1
total_start = 32000
# total_end = 1000000
total_end = 50000
file_name = 'raw_data'
# save_dir = 'data/'
save_dir = 'data2/'
num_sites_upper_limit = 128


def get_space_group(file_id):  # function to get space group by id

    doc = m.get_doc("mp-{}".format(file_id))

    return doc["spacegroup"]["symbol"], doc["spacegroup"]["number"]


def get_bands_info(mp_id):

    # print("Getting {}".format(mp_id))
    try:
        band = m.get_bandstructure_by_material_id(material_id="mp-" + str(mp_id), line_mode=True)
        if band is None:
            return 4
    # error when id is not valid
    except IndexError:
        if verbose:
            # print(str(mp_id) + " is not valid")
            pass
        return 1
    except pymatgen.ext.matproj.MPRestError:
        # print("API_key needs updated, at 1")
        return 2
    else:
        try:
            structure = m.get_structure_by_material_id(material_id="mp-" + str(mp_id))
        except pymatgen.ext.matproj.MPRestError:
            # print("API_key needs updated, at 2")
            return 3

        if structure.num_sites > num_sites_upper_limit:
            return -1
        #print("Found ...")
        save_struct = {}
        save_struct['id'] = mp_id
        save_struct['formula'] = structure.formula
        save_struct['num_sites'] = structure.num_sites
        save_struct['elements'] = [{'name': s.name,
                                'number': s.number,
                                } for s in structure.species]

        save_struct['band'] = {}
        save_struct['band']['bands'] = two_d_format(band.bands[Spin.up].tolist())
        save_struct['band']['branches'] = band.branches

        save_struct['spacegroup'], save_struct['number'] = get_space_group(mp_id)
        # print('saving:', mp_id)

        writejson(save_struct, '../data/raw_data_{}.json'.format(mp_id))

        return 0


def writejson(data, file_name, sort=True):
    with open(file_name, 'w') as f:
        json.dump(data, f, ensure_ascii=False, sort_keys=sort, indent=4, cls=MyEncoder)


def record_mp_ids(data_dir="data/"):
    mp_id_list = []
    for dirs, subdirs, files in os.walk(data_dir):
        for file in files:
            tmp = re.split('\.', file)[0]
            mp_id = int(re.split('_', tmp)[-1])
            mp_id_list.append(mp_id)

    return mp_id_list


def test():
    this_list = record_mp_ids()
    print(this_list)
    print(len(this_list))
    pass

# test()


if __name__ == "#__main__":
    total_count = 0
    valid = 0
    invalid = 0
    large_system =0
    valid_id_list = []
    save_json = True
    mp_ids_list = record_mp_ids(data_dir="../data/")

    print("Start RUNING...")
    # >>>>>>
    for i in range(2100000, 2200000):
        # print('\rrunning:', i, end='')
        if i in mp_ids_list:
            pass
        else:
            state = get_bands_info(i)
            total_count += 1
            if state == 0:
                valid += 1
                valid_id_list.append(i)
                print(f"\rSuccessfully saved:  {i} | Totally saved: {valid} | Total trail: {total_count} ", end='')
            elif state == 1 or state == 4:
                invalid += 1
                print(f"\rInvalid id: {i} | Totally saved: {valid} | Total trail: {total_count}", end='')
            elif state == 2 or state ==3:
                print(f"Need update API_key, check valid_mp_id.jason")
                if save_json:
                    with open("valid_mp_id.json", "w") as f:
                        json.dump(valid_id_list, f, indent=2)
                        save_json = False
            elif state == -1:
                large_system += 1
                print(f"\rLarge system: {i} | Totally saved: {valid} | Total trail: {total_count}", end='')

            print(f"DONE: Total trails {total_count}| Valid trails {valid} | Invalid trails {invalid} | Large system {large_system}")

    with open("valid_mp_id.json", "w") as f:
        json.dump(valid_id_list, f, indent=2)
