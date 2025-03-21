import random

collection = {
    "rnb": {
        "SZA": ["luther", "30 For 30", "Snooze", "Kill Bill"],
        "Babyface": ["Every Time I Close My Eyes", "Lady, Lady", "Illusions"]
    },
    "rock": {
        "Pink Floyd": ["Wish You Were Here", "Comfortably Numb", "Time"],
        "The Beatles": ["Come Together", "Here Comes The Sun", "Here, There And Everywhere"]
    }
}

def add_singer(singer, genre, songs=None):
    """Add a singer with songs to the collection under a specific genre."""
    if songs is None:
        songs = []
    genre = genre.lower()
    if genre not in collection:
        collection[genre] = {}
    if singer in collection[genre]:
        collection[genre][singer].extend(songs)
    else:
        collection[genre][singer] = songs

def random_song(genre=None):
    """Return a random song from a given genre or any genre if not specified."""
    if genre:
        genre = genre.lower()
        if genre not in collection or not collection[genre]:
            return None
        singers = list(collection[genre].keys())
        chosen_singer = random.choice(singers)
        songs = collection[genre][chosen_singer]
        if not songs:
            return None
        return (chosen_singer, random.choice(songs), genre)
    else:
        if not collection:
            return None
        chosen_genre = random.choice(list(collection.keys()))
        return random_song(chosen_genre)

def random_singer(genre=None):
    """Return a random singer from a given genre or any genre if not specified."""
    if genre:
        genre = genre.lower()
        if genre not in collection or not collection[genre]:
            return None
        return random.choice(list(collection[genre].keys()))
    else:
        if not collection:
            return None
        chosen_genre = random.choice(list(collection.keys()))
        return random_singer(chosen_genre)

def find_singer(keyword):
    """Find singers whose name contains the given keyword (case insensitive)."""
    keyword = keyword.lower()
    result = []
    for genre, singers in collection.items():
        for singer in singers.keys():
            if keyword in singer.lower():
                result.append((singer, genre))
    return result
