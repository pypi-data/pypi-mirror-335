import os
from pathlib import Path
import re
import readline  # this is imported to fix input usage
import sys

import requests
from time import sleep

import trulogger

import mutagen
from mutagen.id3 import APIC, TIT2, TALB, TPE1, TPE2, TRCK, TDRC, TPOS, TCON
from mutagen.mp4 import MP4Cover

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from ytmusicapi import YTMusic, setup_oauth

from tru_music.artist_album import ArtistAlbum


# pylint: disable=too-many-instance-attributes
class TruMusic:
    supported_file_extensions = ['mp3', 'm4a']

    field_maps = {
        'MP4': {
            "artist": "\xa9ART",
            "album_artist": "aART",
            "album": "\xa9alb",
            "title": "\xa9nam",
            "year": "\xa9day",
            "track": "trkn",
            "disk": "disk",
            "cover": "covr",
        },
        "MP3": {
            "artist": TPE1,
            "album_artist": TPE2,
            "album": TALB,
            "title": TIT2,
            "year": TDRC,
            "track": TRCK,
            "disk": TPOS,
            "cover": APIC,
            # "genre": TCON,
        }
    }
    max_tries = 3

    # pylint: disable=too-many-arguments
    def __init__(
            self,
            ext: str = '.mp3',
            dry_run: bool = False,
            quiet: bool = False,
            verbose: bool = False,
            artist_name: str = None,
            album_name: str = None,
            link: str = None,
    ):
        self.home = str(Path.home())
        self._base_dest_dir = None
        self._oauth_file = None
        self._yt_music = None
        self._dest_dir = None
        self.artist_name = artist_name
        self.album_name = album_name
        self.link = link

        self.current_filename = None

        self.ext = ext
        self.dry_run = dry_run
        self.logger = trulogger.TruLogger({'verbose': verbose})
        self.quiet = quiet

        self._image_file: str = None

        self.album_info: dict = {}

        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.ext,
            }],
            "progress_hooks": [self.yt_dlp_monitor]
        }

    @property
    def base_dest_dir(self):
        if self._base_dest_dir is None:
            self._base_dest_dir = f"{self.home}/Music/TruMusic"

        if not os.path.isdir(self._base_dest_dir):
            os.makedirs(self._base_dest_dir)

        return self._base_dest_dir

    @base_dest_dir.setter
    def base_dest_dir(self, value):
        self._base_dest_dir = value

    @property
    def oauth_file(self):
        if self._oauth_file is None:
            self._oauth_file = f"{self.home}/.config/ytmusicapi/oauth.json"

        if not os.path.isfile(self._oauth_file):
            # create the oauth file directory if it doesn't exist
            if not os.path.isdir(os.path.dirname(self._oauth_file)):
                os.makedirs(os.path.dirname(self._oauth_file))
            # open the browser to authenticate the user
            setup_oauth(filepath=self._oauth_file, open_browser=True)

        return self._oauth_file

    @oauth_file.setter
    def oauth_file(self, value):
        self._oauth_file = value

    @property
    def dest_dir(self):
        return self._dest_dir

    @dest_dir.setter
    def dest_dir(self, value):
        self._dest_dir = f"{self.base_dest_dir}/{value}"
        if not os.path.exists(self._dest_dir):
            if not self.dry_run:
                os.makedirs(self._dest_dir)

    @property
    def image_file(self):
        return self._image_file

    @image_file.setter
    def image_file(self, cover_url: str):
        img_data = requests.get(cover_url, timeout=30).content
        self._image_file = f"{self.dest_dir}/cover.jpg"
        if not self.dry_run:
            with open(self._image_file, 'wb') as handler:
                handler.write(img_data)

    @property
    def yt_music(self):
        if self._yt_music is None:
            self._yt_music = YTMusic(self.oauth_file)
        return self._yt_music

    def yt_dlp_monitor(self, data):
        if data['status'] == 'finished':
            info_dict = data.get('info_dict')
            self.current_filename = info_dict.get('filename').replace(f".{info_dict.get('ext')}", f".{self.ext}")

    @staticmethod
    def _clean_string(title):
        return re.sub(' +', ' ', re.sub('[/|⧸]', '', title))

    @staticmethod
    def _clean_search_string(title):
        return title.replace('⧸', '/')

    def _set_log_prefix(self, prefix=None):
        _prefix = ""
        if self.dry_run:
            _prefix += "[ DRY RUN ] "
        if prefix is not None:
            if isinstance(prefix, list):
                for item in prefix:
                    _prefix += f"[ {item} ] "
            elif isinstance(prefix, str):
                _prefix += f"[ {prefix} ] "
        self.logger.set_prefix(_prefix)

    def _cleanup(self):
        if self.image_file is not None and os.path.exists(self.image_file):
            os.remove(self.image_file)
            self._image_file = None
            self.album_info = {}

    # pylint: disable=too-many-branches
    def tag_file(self, track_info: dict):
        """
        Tag audio files based on directory structure
        :param track_info: dict of track info
        :return:
        """
        artist = track_info.get("artist")
        album = track_info.get("album")

        track_tags = {
            "artist": artist,
            "album": album,
            "album_artist": artist,
            "year": track_info.get('year'),
            "cover": track_info.get('cover'),
            "title": track_info.get('title'),
            "track": (track_info.get('track_num'), track_info.get("track_count")),
            "disk": (1, 1),
        }

        track_file = track_info.get('filename')

        self.logger.success(f"TAGGING: {track_file}")

        audiofile = mutagen.File(track_file)

        if hasattr(audiofile, "tags"):
            del audiofile.tags
        audiofile.add_tags()

        file_type = audiofile.__class__.__name__
        if file_type not in self.field_maps:
            self.logger.error(f"Unsupported file type: {file_type}")
            return False

        field_map = self.field_maps[file_type]
        for field in field_map:
            if field in track_tags:
                _field = field_map[field]
                if field == "cover":
                    if os.path.exists(track_tags[field]):
                        with open(track_tags[field], "rb") as file_handle:
                            if file_type == "MP4":
                                audiofile.tags[_field] = [
                                    MP4Cover(file_handle.read(), imageformat=MP4Cover.FORMAT_JPEG)
                                ]
                            elif file_type == "MP3":
                                audiofile.tags.add(
                                    APIC(
                                        mime='image/jpeg',
                                        type=3,
                                        desc='Cover',
                                        data=file_handle.read()
                                    )
                                )
                            else:
                                self.logger.warning(f"Unsupported file type (cover art): {file_type}")
                    else:
                        self.logger.warning(f"Album art is missing: {track_tags[field]}")
                else:
                    if file_type == "MP3":
                        if field in ["track", "disk"]:
                            track_tags[field] = f"{track_tags[field][0]}/{track_tags[field][1]}"
                        audiofile.tags[_field] = field_map[field](encoding=3, text=track_tags[field])
                    elif file_type == "MP4":
                        audiofile.tags[_field] = [track_tags[field]]
            else:
                self.logger.warning(f"Field not found in data: {field}")

        if not self.dry_run:
            audiofile.save()

        return True

    # pylint: disable=too-many-branches
    def clean_tags(self, _file_path):
        """
        Tag audio files based on directory structure
        :param _file_path:
        :return:
        """

        self.logger.info(f"CLEANING TAGS: {_file_path}")

        audiofile = mutagen.File(_file_path)

        file_type = audiofile.__class__.__name__
        if file_type not in self.field_maps:
            self.logger.error(f"Unsupported file type: {file_type}")
            return False

        field_map = self.field_maps[file_type]
        # pylint: disable=too-many-nested-blocks
        if hasattr(audiofile, "tags"):
            tags = {}
            for field, _field in field_map.items():
                if _field in audiofile.tags:
                    field_data = audiofile.tags[_field]
                    if field == "cover":
                        if file_type == "MP4":
                            audiofile.tags[_field] = [
                                MP4Cover(field_data, imageformat=MP4Cover.FORMAT_JPEG)
                            ]
                        elif file_type == "MP3":
                            tags[_field] = field_data
                            #audiofile.tags.add(
                            #    APIC(mime='image/jpeg', type=3, desc=u'Cover', data=field_data))
                        else:
                            self.logger.warning(f"Unsupported file type (cover art): {file_type}")
                    else:
                        if file_type == "MP3":
                            module = getattr(sys.modules[__name__], field_map[field])
                            if field in ["track", "disk"]:
                                if str(field_data).endswith("/0") or str(field_data).startswith("0/"):
                                    field_data = "1/1"
                            tags[_field] = module(encoding=3, text=str(field_data))
                        elif file_type == "MP4":
                            tags[_field] = [field_data]
                else:
                    self.logger.warning(f"Field not found in data: {field}/{_field}")
                    if field == "disk":
                        self.logger.info(f"Populating field with default value: {field}/{_field} :: 1/1")
                        if file_type == "MP3":
                            module = getattr(sys.modules[__name__], field_map[field])
                            tags[_field] = module(encoding=3, text="1/1")
                        elif file_type == "MP4":
                            tags[_field] = ["1/1"]
            del audiofile.tags
            audiofile.add_tags()
            for tag in tags.values():
                audiofile.tags.add(tag)
            if not self.dry_run:
                audiofile.save()
        return True

    def _get_artist_albums(self):
        self.logger.info("Collecting albums...")
        search_results = self.yt_music.search(self.artist_name, filter='albums', limit=100)

        matching_titles = []
        for item in search_results:
            self.logger.debug(f"Processing item: {item.get('title')} [{item['browseId']}]")
            if self.album_name is None or self.album_name in item.get('title').lower():
                try:
                    album = self.yt_music.get_album(item['browseId'])
                except Exception:
                    self.logger.warning(f"Error getting album info: {item.get('title')} [{item['browseId']}]")
                    continue
                _artist_album = ArtistAlbum(album=album, item=item)
                if self.artist_name.lower() != _artist_album.artist.lower():
                    continue
                matching_titles.append(_artist_album)
                for other_version in album.get('other_versions', []):
                    self.logger.debug(
                        f"Processing other_version: {other_version.get('title')} [{other_version['browseId']}]"
                    )
                    matching_titles.append(
                        ArtistAlbum(
                            album=self.yt_music.get_album(other_version['browseId']),
                            item=other_version
                        )
                    )

        return matching_titles

    @staticmethod
    def _get_option_string(item: dict, index: int):
        album = item.get('album')
        return f"[{index}] {item.get('item').get('title')} ({album.get('year')} :: {album.get('trackCount')} tracks)"

    def _get_selection(self, matching_titles: list[ArtistAlbum]):
        selected_item = None
        match_count = len(matching_titles)
        if match_count == 1 or (match_count > 0 and self.quiet):
            selected_item = matching_titles[0]
        elif match_count > 1:
            options_list = []
            # build options list
            for index, item in enumerate(matching_titles, 1):
                options_list.append(f"[{index}] {item.option_title}")
            while selected_item is None:
                print("\n".join(options_list))
                selection = input(f"\n{match_count} matching results found; select one (q to quit): ")
                if selection == "q":
                    return False
                if not selection.isnumeric():
                    print(f"Invalid selection {selection}")
                    continue
                # convert to integer and adjust for 0-based index
                selection = int(selection) - 1
                if 0 <= selection < match_count:
                    selected_item = matching_titles[selection]
                else:
                    print(f"Invalid selection {selection + 1}")
        else:
            self.logger.error(f"No match found for \"{self.artist_name}\" - \"{self.album_name}\"")
            return False
        selected_item.display_cover()
        selected_item.display_tracks()
        confirm = input("Download (y/n/q to quit): ")
        if confirm == "q":
            return False
        elif confirm.lower() != "y":
            return self._get_selection(matching_titles)
        return selected_item

    # pylint: disable=too-many-locals)
    def run(self):
        """
        Run process
        """
        if self.link:
            self.logger.info("Processing link...")
            # get the browseId from the link
            list_id = self.link.split("list=")[1]
            # get the browseId for the album
            browse_id = self.yt_music.get_album_browse_id(list_id)
            # get the album info
            album = self.yt_music.get_album(browse_id)
            matching_titles = [
                ArtistAlbum(
                    album=album,
                    item=album
                )
            ]
        else:
            matching_titles = self._get_artist_albums()
        if selected_item := self._get_selection(matching_titles=matching_titles):
            _artist_name = selected_item.artist

            self.dest_dir = f"{_artist_name}/{selected_item.title}"
            self.image_file = selected_item.cover_url

            self.logger.info(selected_item.option_title)
            self._set_log_prefix([_artist_name, selected_item.title])
            tracks_to_download = selected_item.tracks
            tries = 0
            failures = []
            while tracks_to_download and tries <= self.max_tries:
                tries += 1
                self.logger.info(f"TRY {tries}/{self.max_tries}")
                num_tracks = len(tracks_to_download)
                failures = []
                for index, track in enumerate(tracks_to_download, 1):
                    track_num = str(index).zfill(2)
                    self.logger.info(
                        f"DOWNLOADING {index}/{num_tracks}: {track_num} - {track['title']}{' [E]' if track['isExplicit'] else ''}"
                        f" ({track['duration']})"
                    )
                    if not self.dry_run:
                        self.ydl_opts['outtmpl'] = f"{self.dest_dir}/{track_num} - {track.get('title')}.%(ext)s"
                        with YoutubeDL(self.ydl_opts) as ydl:
                            track_tries = 0
                            while track_tries <= self.max_tries:
                                track_tries += 1
                                try:
                                    ydl.download([f"https://music.youtube.com/watch?v={track.get('videoId')}"])
                                    self.tag_file({
                                        "title": track.get('title'),
                                        "artist": _artist_name,
                                        "album": selected_item.title,
                                        "album_artist": _artist_name,
                                        "year": selected_item.year,
                                        "cover": self.image_file,
                                        "track_num": index,
                                        "track_count": selected_item.track_count,
                                        "filename": self.current_filename,
                                    })
                                    break
                                except DownloadError as dle:
                                    self.logger.error(f"Download error: {dle}")
                                    self.logger.error(f"Track Try {tries}/{self.max_tries} failed: {track.get('title')}")
                                    sleep(5)
                            if tries >= self.max_tries:
                                failures.append(track)
                                self.logger.error(f"Max track tries reached, skipping: {track.get('title')}")
                tracks_to_download = failures
            self._cleanup()
            if failures:
                self.logger.error(f"Max tries reached, skipping failed tracks:")
                for failed_track in failures:
                    self.logger.error(f"\t{failed_track.get('title')}")
                return False
            return True
        return False
