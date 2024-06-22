import discogs_client
import os
import sys
import typing
import yaml

path = sys.argv[1]
with open(path, "r") as file:
    input = yaml.safe_load(file)

token = os.getenv("DISCOGS_TOKEN")
if token is None:
    raise RuntimeError("Must set DISCOGS_TOKEN. See https://www.discogs.com/settings/developers")

client = discogs_client.Client("DlAlbum/0.1 +https://github.com/trikil/dl-album", user_token=token)

output = []
for album in input:
    if "id" not in album:
        continue
    id = album["id"]
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
    for x in album:
        if x == "hint":
            continue
        new_album[x] = album[x]
    output.append(new_album)

    album["hint"] = new_album["artist"] + " -- " + new_album["title"]

with open(path, "w") as file:
    yaml.dump(input, file)
yaml.dump(output, sys.stdout)