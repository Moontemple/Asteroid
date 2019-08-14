from src.main.web.flaskserv.Database import MusicDB
import os
import exiftool


def clear(path):
    """
    TODO
    """
    if os.path.isfile(path):
        os.remove(path)


def get_song_item(song_path):
    """
    TODO
    """
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata(song_path)

    artist = metadata["RIFF:Artist"]
    title = metadata["RIFF:Title"]
    duration = metadata["Composite:Duration"]

    return {'name': title, 'artist': artist, 'duration': duration, 'file_path': song_path, 'meta_dat': ''}


def list_wav(path):
    """
    TODO
    """
    files = [os.path.join(path, f) for f in os.listdir(
        path) if os.path.isfile(os.path.join(path, f)) and '.wav' in f]
    return files


def build_music(folder_location):
    """
    TODO
    """
    dbinst = MusicDB()

    if folder_location == None:
        return

    for file in list_wav(folder_location):
        try:
            song = get_song_item(file)
            dbinst.add_song(song)
        except Exception as e:  # TODO, song doesn't exist if fails
            print("[!] trying to add song '{}', raised exception: \n\t\t'{}'".format(song['name'], str(e)))
        else:
            print("[+] added '{}' by '{}' @ '{}' to database".format(song['name'], song['artist'], song['file_path']))
