import urllib.parse


def make_search_url(query: str) -> str:
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.songsterr.com/?pattern={encoded}"


def make_chords_url(song_id: int) -> str:
    return f"https://www.songsterr.com/a/wsa/{song_id}?inst=guitar"