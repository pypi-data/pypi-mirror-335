#example
import songsingergenerator.music as music
def main():
    music.addSinger("Khalil Fong", "neosoul",["Love Song", "SingalongSong"])
    result = music.randomSong("neosoul")
    print("result song: ", result)


if __name__ == "__main__":
    main()