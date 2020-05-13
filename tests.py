from piano import Piano, Ukutabs

piano = Piano()

assert(piano.get_interval("A", "M4") == "D")
assert(piano.get_interval("A", "-M4") == "E")

assert(piano.chord_to_major_key("A") == ["A", "D", "E"])
assert(piano.chord_to_major_key("C") == ["C", "F", "G"])
assert(piano.chord_to_major_key("Bb") == ["Bb", "Eb", "F"])
assert(piano.chord_to_major_key("A#") == ["Bb","Eb", "F", ])
assert(piano.chord_to_major_key("Am") == ["C", "F"])

judge_url = "https://ukutabs.com/t/twenty-one-pilots/the-judge/"
riptide_url = "https://ukutabs.com/v/vance-joy/riptide/"
delilah_url = "https://ukutabs.com/p/plain-white-ts/hey-there-delilah/"

ukutabs = Ukutabs()

urls = [judge_url, riptide_url, delilah_url]
chords = [ukutabs.get_chords(url) for url in urls]
keys = [piano.get_key_from_chords(chord) for chord in chords]

assert(keys == ["C", "Db" , "D"])

chords = ["Amsus", "C", "F", "Em"]
assert(piano.get_chord_numbers(chords, "C") == ["vi", "I", "IV", "iii"])


