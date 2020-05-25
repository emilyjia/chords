from bs4 import BeautifulSoup
from requests import get
from collections import Counter
import re
import json
from dotenv import load_dotenv
import spotipy
import spotipy.util as util
load_dotenv()

class Piano:
    keyboard = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    intervals = ["M1", "m2", "M2", "m3", "M3", "M4", "m5", "M5", "m6", "M6", "m7", "M7"]
    number_to_roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}
    interval_to_halfstep = {interval: halfstep for halfstep, interval \
                                 in enumerate(intervals)}
    halfstep_to_interval = {halfstep: interval for halfstep, interval \
                                  in enumerate(intervals)}
    map_to_keyboard = {}
    for i, key in enumerate(keyboard):
        if "b" in key:
            map_to_keyboard[keyboard[i-1] + "#"] = keyboard[i]
        map_to_keyboard[key] = key

    def __init__(self):
        pass

    # intervals can be -m2 or m2
    # assumes that start is in keyboard
    def get_interval(self, start, interval_name):
        assert(start in self.keyboard)
        down = -1 if "-" in interval_name else 1
        interval = interval_name[1:] if down == -1 else interval_name
        start_halfstep = self.keyboard.index(start)
        halfsteps = down * self.interval_to_halfstep[interval]
        return self.keyboard[(start_halfstep + halfsteps) % len(self.keyboard)]

    ##
    def clean_chord(self, chord):
        minor = ("m" in chord) and ("maj" not in chord)
        if len(chord) > 1 and chord[1] in ["b", "#"]:
            chord = chord[:2]
        else:
            chord = chord[0]
        chord = self.map_to_keyboard[chord]
        return chord, minor

    # chord to major key
    # hypothesis: identifying I, iii, IV, V, vi is enough
    def chord_to_major_key(self, chord):
        chord, minor = self.clean_chord(chord)
        if not minor:
            I_chord = chord
            IV_chord = self.get_interval(chord, "-M4")
            V_chord = self.get_interval(chord, "-M5")
            chords = [I_chord, IV_chord, V_chord]
            chords.sort()
            return chords
        else:
            iii_chord = self.get_interval(chord, "-M3")
            vi_chord = self.get_interval(chord, "-M6")
            chords = [iii_chord, vi_chord]
            chords.sort()
            return chords

    def get_major_key_from_chords(self, chords):
        key_frequencies = Counter()
        vi_count = 0
        I_count = 0
        for chord in chords:
            chord_major_keys = self.chord_to_major_key(chord)
            for key in chord_major_keys:
                key_frequencies[key] += 1
        return key_frequencies.most_common(1)[0][0]

    def get_interval_between(self, low, high):
        halfsteps = (self.keyboard.index(high) - self.keyboard.index(low)) % len(self.keyboard)
        return self.halfstep_to_interval[halfsteps]

    def get_chord_numbers(self, chords):
        key = self.get_major_key_from_chords(chords)
        chord_numbers = []
        for chord in chords:
            chord, minor = self.clean_chord(chord)
            interval = self.get_interval_between(key, chord)[1]
            chord_number = self.number_to_roman[int(interval)]
            if minor:
                chord_number = chord_number.lower()
            chord_numbers.append(chord_number)
        return chord_numbers

    def get_pattern(self, chord_numbers):
        best_pattern_freq = 0
        best_pattern = None
        best_pattern_length = 0
        for pattern_length in range(2, 7):
            # looks at chord progressions of length pattern_length
            lines = [chord_numbers[i: i+pattern_length] for i in range(len(chord_numbers) - pattern_length)]
            filtered_lines = []
            # sort each chord progression and keep if distinct
            for line in lines:
                line.sort()
                distinct = True
                for j in range(len(line) - 1):
                    distinct = distinct and (line[j] != line[j+1])
                if distinct:
                    filtered_lines.append("/".join(line))
            # note frequency of most common chord progression
            if len(filtered_lines) > 0:
                freqs = Counter(filtered_lines)
                pattern, freq = freqs.most_common(1)[0]
                if freq > best_pattern_freq:
                    best_pattern_freq = freq
                    best_pattern = freqs
                    best_pattern_length = pattern_length
        return (best_pattern, best_pattern_length)

class Ukutabs:
    def __init__(self):
        pass

    def get_chords_from_url(self, url):
        response = get(url)
        soup = BeautifulSoup(response.text, features = "lxml")
        chords = [x["name"] for x in soup.select(".hoverchord")]
        return chords

    def get_chords_from_song_info(self, artist, song_name):
        artist = artist.replace(" ", "-")
        # remove anything after "(" or "-"
        song_name = song_name.split(" (")[0]
        song_name = song_name.split(" -")[0]
        # remove punctuation
        song_name = song_name.replace("’", "")
        url = "https://ukutabs.com/" + artist[0] + "/" + artist + "/" + song_name + "/"
        chords = ukutabs.get_chords(url)
        return chords

class UltimateGuitar:
    def __init__(self):
        pass

    def get_chords_from_url(self, url):
        response = get(url)
        soup = BeautifulSoup(response.text, features = "lxml")
        chords = str(soup).split("[tab]", 1)[1].split("[ch]")
        clean_chords = []
        for i, chord in enumerate(chords):
            if "[/ch]" in chord:
                clean_chords.append(chord.split("[/ch]")[0])
        return clean_chords

    def get_chords_from_song_info(self, artist, song_name):
        found = False
        # remove anything after "(" or "-"
        song_name = song_name.split(" (")[0]
        song_name = song_name.split(" -")[0]
        # remove punctuation
        song_name = song_name.replace("’", "")
        url = "https://www.ultimate-guitar.com/search.php?search_type=title&value="
        for word in artist.split(" ") + song_name.split(" "):
            url += word
            url += "%20"
        response = get(url)
        soup = BeautifulSoup(response.text, features = "lxml")
        chords_div = soup.find_all("div", {"class": "js-store"})[0]
        d= json.loads(chords_div.get("data-content"))
        for song in d["store"]["page"]["data"]["results"]:
            song_url = song["tab_url"]
            if song_name.lower() in song["song_name"].lower() and "/pro/" not in song_url:
                return self.get_chords_from_url(song_url)



class Playlist:
    def __init__(self, username, playlist_name):
        self.username = username
        # assumes that client_id, client_secret, redirect_uri are in OS environment
        self.token = util.prompt_for_user_token(username)
        self.sp = spotipy.Spotify(auth = self.token)
        self.piano = Piano()
        self.ug = UltimateGuitar()
        self.playlist_name = playlist_name
        self.playlist_id = self.get_playlist_id()

    def get_playlist_id(self):
        playlists = self.sp.user_playlists(self.username)['items']
        for playlist in playlists:
            if playlist["name"].lower() == self.playlist_name.lower():
                return playlist["id"]
        raise ValueError('playlist not found')

    def get_playlist_songs(self):
        results = self.sp.playlist(self.playlist_id, fields="tracks,next")
        tracks = results['tracks']
        artists = []
        songs = []
        for item in tracks['items']:
            track = item['track']
            artists.append(track['artists'][0]['name'])
            songs.append(track['name'])
        return list(zip(artists, songs))

    def get_playlist_chords(self):
        playlist_songs = self.get_playlist_songs()
        playlist_chords = []
        playlist_titles = []
        for artist, title in playlist_songs:
            chords = self.ug.get_chords_from_song_info(artist, title)
            if chords:
                playlist_chords.append(chords)
                playlist_titles.append(title)
        return playlist_titles, playlist_chords

    def get_playlist_patterns(self):
        playlist_titles, playlist_chords = self.get_playlist_chords()
        chord_numbers = list(map(self.piano.get_chord_numbers, playlist_chords))
        patterns = list(map(self.piano.get_pattern, chord_numbers))
        most_common_pattern = list(map(lambda x: x[0].most_common(1)[0][0], patterns))
        return playlist_titles, most_common_pattern

