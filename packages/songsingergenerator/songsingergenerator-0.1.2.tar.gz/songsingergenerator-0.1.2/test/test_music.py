import pytest
from songsingergenerator import music

@pytest.fixture(autouse=True)
def reset_collection():
    music.collection.clear()
    music.collection.update({
        "rnb": {
            "SZA": ["luther", "30 For 30", "Snooze", "Kill Bill"],
            "Babyface": ["Every Time I Close My Eyes", "Lady, Lady", "Illusions"]
        },
        "rock": {
            "Pink Floyd": ["Wish You Were Here", "Comfortably Numb", "Time"],
            "The Beatles": ["Come Together", "Here Comes The Sun", "Here, There And Everywhere"]
        }
    })
    yield

def test_add_singer_new_existing_genre():
    music.add_singer("Test Singer", "rnb", ["Song A", "Song B"])
    assert "Test Singer" in music.collection["rnb"]
    assert "Song A" in music.collection["rnb"]["Test Singer"]

def test_add_singer_new_genre():
    music.add_singer("Test Singer", "pop", ["Song A"])
    assert "pop" in music.collection
    assert "Test Singer" in music.collection["pop"]
    assert music.collection["pop"]["Test Singer"] == ["Song A"]

def test_add_singer_extend_existing():
    music.add_singer("Test Singer", "rnb", ["Song A"])
    music.add_singer("Test Singer", "rnb", ["Song B", "Song C"])
    assert music.collection["rnb"]["Test Singer"] == ["Song A", "Song B", "Song C"]

def test_random_song_single_song():
    music.add_singer("Test Singer", "pop", ["Song A"])
    result = music.random_song("pop")
    assert result is not None
    singer, song, genre = result
    assert singer == "Test Singer"
    assert song == "Song A"
    assert genre == "pop"

def test_random_song_invalid_genre():
    result = music.random_song("classical")
    assert result is None

def test_random_song_empty_songs():
    music.add_singer("Empty Singer", "jazz", [])
    result = music.random_song("jazz")
    assert result is None

def test_random_song_no_genre_specified():
    result = music.random_song()
    assert result is not None
    singer, song, genre = result
    assert genre in music.collection
    assert singer in music.collection[genre]
    assert song in music.collection[genre][singer]


def test_random_singer_single():
    music.add_singer("Test Singer", "pop")
    singer = music.random_singer("pop")
    assert singer == "Test Singer"

def test_random_singer_invalid_genre():
    singer = music.random_singer("classical")
    assert singer is None

def test_random_singer_no_genre_specified():
    music.add_singer("Unique Singer", "jazz")
    singer = music.random_singer()
    assert singer is not None


def test_find_singer_found():
    music.add_singer("Test Artist", "pop")
    results = music.find_singer("Test")
    assert ("Test Artist", "pop") in results

def test_find_singer_case_insensitive():
    music.add_singer("MixedCase Singer", "rock")
    results = music.find_singer("mixedcase")
    assert ("MixedCase Singer", "rock") in results

def test_find_singer_not_found():
    results = music.find_singer("nonexistent")
    assert results == []
