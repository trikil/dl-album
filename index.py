import os
import sys
from typing import Callable
import yaml

import discogs
import dl

def log(string: str):
    print(string, file=sys.stderr)

def prompt(string: str, map = lambda x: x):
    while True:
        x = input(string).strip()
        result = None
        try:
            result = map(x)
        except:
            result = None
        if result != None:
            return result
        log("Sorry, try again")

def main():
    input_path: str = prompt("Enter path of input file (default: ./input.yaml): ")
    if input_path == "":
        input_path = "./input.yaml"
    
    data_path: str = prompt("Enter path of data file (default: ./data.yaml): ")
    if data_path == "":
        data_path = "./data.yaml"
    
    output_path: str = prompt("Enter path of output directory (default: ./files): ")
    if output_path == "":
        output_path = "./files"
    
    use_discogs: int = prompt(
        "Do you want to generate some metadata from Discogs?\n(1) Yes\n(2) Yes; re-download\n(3) No\n(default: 1): ",
        lambda x: 1 if x == "" else int(x) if 0 < int(x) < 4 else None
    )
    DISCOGS_YES = 1
    DISCOGS_YES_ALL = 2
    DISCOGS_NO = 3

    do_download: int = 1
    DOWNLOAD_YES = 1
    DOWNLOAD_NO = 2    
    if use_discogs != DISCOGS_NO:
        discogs_path: str = prompt("Enter path of Discogs data file (default: ./discogs.yaml): ")
        if discogs_path == "":
            discogs_path = "./discogs.yaml"
    
        do_download = prompt(
            "Do you want to actually download the music afterwards?\n(1) Yes\n(2) No\n(default: 1): ",
            lambda x: 1 if x == "" else int(x) if 0 < int(x) < 3 else None
        )
    
        discogs.main(discogs_path, data_path, use_discogs == DISCOGS_YES_ALL)
    
    # copy manual input over to data

    with open(input_path, "r") as file:
        input = yaml.safe_load(file)
    
    if os.path.isfile(data_path):
        with open(data_path, "r") as file:
            data = yaml.safe_load(file)
    else:
        data = {}
    
    for k in input:
        if k in data:
            data[k] = {**input[k], **data[k]}
        else:
            data[k] = input[k]
    
    with open(data_path, "w") as file:
        yaml.dump(data, file)

    if do_download == DOWNLOAD_YES:
        dl.main(data_path, output_path)

if __name__ == "__main__":
    main()