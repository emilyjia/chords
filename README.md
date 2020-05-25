# chords project

Given a spotify username and playlist name, returns the chord progressions for songs in the playlist.

## inspo

I've been playing a lot of ukulele to keep me sane during my job search. Many of my favorite songs use similar chord progressions. I wondered what the true distribution of chord progressions was across my playlists. 

## example
I've made a test playlist with two of my favorite songs: Riptide (Vance Joy) and Stacy (Quinn XCII). I found my username from my spotify profile URL. Let's look at the first five chords in every song. 

__Input__
```python
from piano import Playlist
username = "1276262582"
playlist_name = "Chords Project Test"
playlist = Playlist(username, playlist_name)
titles, chords = playlist.get_playlist_chords()
for title, chord in zip(titles, chords):
    print(title)
    print(chord[:5])
```

__Output__
```
Riptide
['Em', 'Dadd9', 'G', 'Em', 'Dadd9']
Stacy
['A', 'E', 'E', 'F#m', 'D']
```

Now let's look at the estimated chord progressions.

__Input__

```python
playlist.get_playlist_patterns()
```

__Output__
```
(['Riptide', 'Stacy'], ['I/V/vi', 'I/IV/V/vi'])
```

## todo

- Add examples
- Add major/minor key identifier. Current guesser identifies the major key, so the chord numbers look wonky for minor songs.
- Improve pattern detection. Songs commonly have multiple chord progressions of varying lengths. I currently assume that the progression does not have repeat chords (e.g. I would miss I/I/IV/V) and has fixed length. 
- More chord information (e.g. currently read Asus9 as A)
- Playlist creation 





