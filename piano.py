from bs4 import BeautifulSoup
from requests import get
from collections import Counter
import re

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
        minor = ("m" in chord)
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

    def get_key_from_chords(self, chords):
        key_frequencies = Counter()
        for chord in chords:
            chord_major_keys = self.chord_to_major_key(chord)
            for key in chord_major_keys:
                key_frequencies[key] += 1
        return key_frequencies.most_common(1)[0][0]

    def get_interval_between(self, low, high):
        halfsteps = (self.keyboard.index(high) - self.keyboard.index(low)) % len(self.keyboard)
        return self.halfstep_to_interval[halfsteps]

    def get_chord_numbers(self, chords, key):
        chord_numbers = []
        for chord in chords:
            chord, minor = self.clean_chord(chord)
            interval = self.get_interval_between(key, chord)[1]
            chord_number = self.number_to_roman[int(interval)]
            if minor:
                chord_number = chord_number.lower()
            chord_numbers.append(chord_number)
        return chord_numbers

class Ukutabs():
    def __init__(self):
        pass

    def get_chords(self, url):
        response = get(url)
        soup = BeautifulSoup(response.text, features = "lxml")
        chords = [x["name"] for x in soup.select(".hoverchord")]
        return chords


