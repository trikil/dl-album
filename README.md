# `dl-album`

## What is this?

This script downloads albums from popular music streaming sites (using [yt-dlp](https://github.com/yt-dlp/yt-dlp)) and adds custom metadata to each track (using [FFmpeg](https://ffmpeg.org/)). This ensures that metadata is relatively consistent; when downloading music manually from different sources you often get lots of duplicate artists due to varying spelling conventions.

Look at `data.yaml` to see how to specify metadata and download links.

Some audio formats / sites might not yet work; I'll add support as I encounter them.

In the future I'd like to have `data.yaml` be generated from [Discogs](https://www.discogs.com/) data.

## Build

Requires [Docker](https://www.docker.com/).

```sh
docker build -t dl-album --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .
```

## Run

```sh
docker run -v ./data.yaml:/app/data.yaml -v ./files:/app/files -it --rm dl-album
```

This will look for metadata in `./data.yaml` and albums in `./files`. Change as appropriate for your case.