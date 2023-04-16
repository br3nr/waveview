import re

def check_string(input_string):
    youtube_pattern = re.compile(
        (
            r"https?://(www\.)?(youtube|youtu)(\.com|\.be)/"
            "(playlist\?list=|watch\?v=|embed/|)([a-zA-Z0-9-_]+)(\&t=\d+s)?"
            "|https://youtu.be/([a-zA-Z0-9-_]+)(\?t=\d+s)?"
        )
    )
    spotify_pattern = re.compile(
        (
            r"https?://open\.spotify\.com/(album|playlist|track)"
            "/([a-zA-Z0-9-]+)(/[a-zA-Z0-9-]+)?(\?.*)?"
        )
    )

    youtube_match = youtube_pattern.match(input_string)
    spotify_match = spotify_pattern.match(input_string)

    if youtube_match:
        return get_youtube_pattern(youtube_match)
    elif spotify_match:
        return get_spotify_pattern(spotify_match)
    return "Text"


def get_spotify_pattern(spotify_match):
    if spotify_match:
        if "track" in spotify_match.group():
            return "Spotify Track"
        elif "playlist" in spotify_match.group():
            return "Spotify Playlist"
        elif "album" in spotify_match.group():
            return "Spotify Album"
        else:
            return "Spotify URL"


def get_youtube_pattern(youtube_match):
    if youtube_match:
        if "watch?v=" in youtube_match.group() or "youtu.be" in youtube_match.group():
            return "YouTube Song"
        elif "playlist?list=" in youtube_match.group():
            return "YouTube Playlist"
        else:
            return "YouTube URL"