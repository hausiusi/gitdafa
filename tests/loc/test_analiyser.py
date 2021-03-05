import json
import os
import sys

sys.path.append("./")

import loc

current_dir = os.path.dirname(os.path.realpath(__file__))
struct_path = os.path.join(current_dir, 'structs')
samples_path = os.path.join(current_dir, 'samples')
files = os.listdir(struct_path)


def get_files():
    for file_name in files:
        file_path = os.path.join(struct_path, file_name)
        with open(file_path, 'r') as f:
            data = json.load(f)
        sample_path = data['sample_path']
        test_data = data['test_data']
        yield {'sample_path': sample_path, 'test_data': test_data}


def test_CodeFileAnalyzer():
    for file_data in get_files():
        sample_path = os.path.join(samples_path, file_data['sample_path'])
        analize = loc.LineCounter(sample_path)
        for tp in file_data['test_data']:
            fields = file_data['test_data'][tp]
            for field in fields:
                assert fields[field] == analize.result[tp][field]

