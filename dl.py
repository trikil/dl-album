#!/usr/bin/env python3

import os
import pathvalidate
import subprocess
import sys
import tldextract
import yaml


def load_yaml(path, mode):
	with open(path, mode) as stream:
		try:
			return yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			print(exc, file=sys.stderr)
			sys.exit(1)


def download(path, data):
	for album in data:
		if "artist" not in album or "title" not in album:
			continue
		artist = pathvalidate.sanitize_filename(album["artist"])
		album_name = pathvalidate.sanitize_filename(album["title"])
		# if isinstance(value, dict) and "url" not in value:
		# 	handle_folder(path + [key], value)
		# else:

		album_path_arr = path + [artist, album_name]
		album_path = "/".join(album_path_arr)
		if os.path.exists(album_path):
			print("already downloaded: " + album_path)
		else:
			print("now downloading: " + album_path)
			os.makedirs(album_path)
			url = tldextract.extract(album["url"])
			subprocess.run(get_command(url) + [album["url"]], cwd=album_path, stdout=subprocess.DEVNULL)
		for file in os.listdir(album_path):
			file_path = "/".join(album_path_arr + [file])
			set_metadata(album, file_path)


def get_command(url):
	if url.domain == "bandcamp":
		return ["yt-dlp", "--embed-thumbnail", "--embed-metadata"]
	elif url.domain == "youtube":
		return ["yt-dlp", "-x", "--embed-thumbnail", "--embed-metadata", "--parse-metadata", "playlist_index:%(track_number)s"]
	else:
		raise Exception("unknown host " + url.domain)


def set_metadata(data, file_path):
	tags = {}
	if "artist" in data:
		tags["album_artist"] = data["artist"]
		tags["artist"] = data["artist"]
	if "title" in data:
		tags["album"] = data["title"]
	if "released" in data:
		tags["date"] = data["released"]
	
	metadata = []

	for key, value in tags.items():
		escaped = value.replace("\"", "\\\"")
		metadata += ["-metadata", f"{key}={escaped}"]

	file_name, extension = file_path.rsplit(".", 1)

	# ffmpeg doesn't support setting cover image on opus
	# https://trac.ffmpeg.org/ticket/4448
	if extension == "opus":
		extension = "mp3"
		new_file_path = f"{file_name}.{extension}"
		opus_metadata = ffprobe(["-show_streams", file_path])["streams"][0]
		title = opus_metadata["tags"]["title"]
		track = opus_metadata["tags"]["track"]
		ffmpeg([
			"-i", file_path,
			"-c:a", "libmp3lame",
			"-metadata", f"title={title}",
			"-metadata", f"track={track}",
			new_file_path
		])
		run(["rm", file_path])
		file_path = new_file_path

	out_path = file_path # file_path.rsplit(".", 1)[0] + ".flac"
	tmp_audio_path = f"/tmp/audio.{extension}"
	tmp_cover_path = "/tmp/cover.png"

	inputs = ["-i", file_path]

	if "cover" in data:
		run(["wget", "-nv", data["cover"], "-O", tmp_cover_path])
		inputs += ["-i", tmp_cover_path]
		metadata += [
			"-map", "1",
			"-metadata:s:v", "title=\"Album cover\"",
			"-metadata:s:v", "comment=\"Cover (front)\"",
			"-disposition:v", "attached_pic"
		]

	ffmpeg([
		*inputs,
		"-c", "copy",
		"-map", "0:a",
		"-map_metadata", "0",
		*metadata,
		tmp_audio_path
	])

	run(["rm", file_path])
	run(["mv", tmp_audio_path, out_path])


def ffmpeg(args):
	run([
		"ffmpeg",
		"-y", "-hide_banner",
		"-loglevel", "warning",
		*args
	])


def ffprobe(args):
	return yaml.safe_load(subprocess.run([
		"ffprobe",
		"-v", "quiet",
		"-hide_banner",
		"-print_format", "json",
		*args
	], stdout=subprocess.PIPE).stdout)


def run(args):
	subprocess.run(args, stdout=subprocess.DEVNULL)


if __name__ == "__main__":
	data = load_yaml("data.yaml", "r")
	download([".", "files"], data)
