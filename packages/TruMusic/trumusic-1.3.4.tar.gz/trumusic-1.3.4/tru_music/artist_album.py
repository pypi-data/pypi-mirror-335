from ascii_magic import AsciiArt

class ArtistAlbum:

    def __init__(self, item, album):
        artists = item.get('artists')
        # for some reason the artist is at index 1 for regular versions and index 0 for "other_versions"
        self.artist = artists[1].get('name') if len(artists) > 1 else artists[0].get('name')
        self.explicit = item.get('isExplicit')
        self.year = album.get('year')
        self.track_count = album.get('trackCount')
        self._cover_url = None
        self.cover_url = album.get("thumbnails")
        self.tracks = album.get("tracks")
        self.title = item.get('title')

    @property
    def option_title(self):
        return f"{self.title}{' [E]' if self.explicit else ''} ({self.year}) :: {self.track_count} tracks)"

    @property
    def cover_url(self):
        return self._cover_url

    @cover_url.setter
    def cover_url(self, thumbnails):
        _thumbnails = {thumbnail.get("width"): thumbnail.get("url") for thumbnail in thumbnails}
        self._cover_url = _thumbnails.get(max(_thumbnails))

    def display_cover(self):
        my_art = AsciiArt.from_url(self.cover_url)
        my_art.to_terminal(width_ratio=2.5, columns=150)

    def display_tracks(self):
        for index, track in enumerate(self.tracks, 1):
            print(
                f"{str(index).zfill(2)} - {track['title']}{' [E]' if track['isExplicit'] else ''} ({track['duration']})"
            )
