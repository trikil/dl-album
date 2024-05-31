## What is this?

This script downloads albums from popular music sites and adds custom metadata to each track.

Look at `data.yaml` to see how to specify that metadata.

In the future I'd like to have `data.yaml` be generated from [Discogs](https://www.discogs.com/) data.

## Build

Requires [Docker](https://www.docker.com/).

```sh
docker build -t dl-album .
```

## Run

```sh
docker run -v ./data.yaml:/app/data.yaml -v ./files:/app/files -it --rm dl-album
```

This will look for metadata in `./data.yaml` and albums in `./files`. Change as appropriate for your case.