import os
import json

list_dir = "word_search"
worker_dir = os.getcwd()
word_list="wordList.json"


word_list_path = os.path.join(worker_dir, list_dir, word_list)


def check_folder():
    # check if folder exists, create if false
    if not os.path.exists(os.path.join(worker_dir, list_dir)):
        os.mkdir(os.path.join(worker_dir, list_dir))


def check_files():
    # check if files exist, create if false
    if not os.path.exists(word_list_path):
        open(word_list_path, 'w')
        empty_file = {
            "white":[],
            "black":[]
        }
        with open(word_list_path, "w") as f:
            json.dump(empty_file, f)


def read_files():
    with open(word_list_path, "r") as f:
        data = json.load(f)
    return data


def add_word_new(value, color):
    with open(word_list_path, "r") as f:
        data = json.load(f)

    data[color].append(value)

    with open(word_list_path, "w") as f:
        json.dump(data, f)

def delete_word(value_to_delete, list):
    with open(word_list_path, "r") as f:
        data = json.load(f)
    data[list].remove(value_to_delete)
    with open(word_list_path, "w") as f:
        json.dump(data, f)
