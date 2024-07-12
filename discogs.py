import argparse
import discogs_client
import os
import sys
import time
import typing
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml import YAML


def main(input_path: str, output_path: str, retag_all: bool):
    yaml = YAML()
    yaml.width = float("Infinity")
    with open(input_path, "r") as file:
        input: dict = yaml.load(file)
    if os.path.isfile(output_path):
        with open(output_path, "r") as file:
            output = yaml.load(file)
    else:
        output = []

    token = os.getenv("DISCOGS_TOKEN")
    if token is None:
        raise RuntimeError("Must set DISCOGS_TOKEN. See https://www.discogs.com/settings/developers")

    client = discogs_client.Client("DlAlbum/0.1 +https://github.com/trikil/dl-album", user_token=token)

    for id, album in input.items():
        # if "hint" in album:
        #    continue

        indices = [i for i, a in enumerate(output) if "discogs_id" in a and a["discogs_id"] == id]
        if len(indices) > 0 and not retag_all:
            continue

        print(f"{id}: {album}", file=sys.stderr)

        if type(album) is str:
            split = album.split(None, 1)
            if len(split) == 1:
                url = split[0]
                hint = None
            else:
                url, hint = split
        else:
            raise RuntimeError("bleh")
        
        time.sleep(2)

        if type(id) is int:
            id = f"r{id}"
        
        letter = id[0]
        number = id[1:]

        if letter == "m":
            release = typing.cast(discogs_client.Release, client.master(number).main_release)
        elif letter == "r":
            release = client.release(number)
        else:
            raise RuntimeError("Discogs id must be Master or Release")
        
        new_album = {}
        new_album["cover"] = release.images[0]["resource_url"] # type: ignore 
        new_album["artist"] = release.artists[0].name # type: ignore
        new_album["title"] = release.title
        new_album["released"] = release.year
        new_album["url"] = url
        new_album["discogs_id"] = id

        output.append(new_album)
        with open(args.output, "w") as file:
            yaml.dump(output, file)

        sorted_input = CommentedMap()
        for id in sorted(input.keys(), key=lambda id: sort_fn(id, output)):
            print(input[id])
            sorted_input[id] = input[id]

        with open(args.input, "w") as file:
            yaml.dump(sorted_input, file)


def sort_fn(id: str, output: list):
    album = [a for a in output if "discogs_id" in a and a["discogs_id"] == id][0]
    return album["artist"], album["released"], album["title"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="discogs.py",
        description="Download album metadata from Discogs",
    )

    parser.add_argument("input", default=sys.stdin)
    parser.add_argument("output", default=sys.stdout)
    parser.add_argument("-a", "--all", action="store_true")

    args = parser.parse_args()
    main(args.input, args.output, args.all)