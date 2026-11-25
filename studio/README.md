# Studio: animated series for Red Ink Episodes

Handover for continuing the work in a new Claude chat. The channel is **Red Ink Episodes**
(Instagram + YouTube @RedInkEpisodes). Episodes are posted by `.github/workflows/series.yml`
(`scripts/series.py` reads `series/queue.json`, 1 episode a day at 19:07 via Buffer).

## Series 1: UNRANKED (done)
12 episodes, silhouette style, already in `series/unranked/` and the queue.

## Series 2: MY SLIME EATS BOSSES (in progress)
Vertical 9:16, 3-4 min episodes, narrated in English (Speko TTS, voice "Charon",
model gemini-3.8-flash-lite-tts, provider google-tts, brisk storyteller).

**What the user wants:** constant hooks and cliffhangers, an underdog payoff, the slime's power
revealed slowly (only when the hero is abandoned in a crisis), a professional look, no click on every
cut. The user asked Claude to act as director. Inspired by (not copying) the "100% Drop rate" series.

### Episode 1 (finished in `studio/slime-ep1/`)
Brindle village. In 7 days every pet is weighed on the Pet Stone: over 100 power gets a guild contract
(food for the family), under 100 the guild takes the pet. Poor Milo (mom, little sister Pip, 3 coins)
has Bob, a slime with power 2 who eats everything. One hint: Bob swallows a rusty sword and his eyes
look metal for a second. Bounty: Rat King LV12, 50 gold. Rolf (mayor's son, drake) takes Milo as bait,
Tess and her wolf Ash come too. In the sewer Ash is thrown, Rolf pushes Milo back and locks the gate.
Alone in the dark, Milo tells Bob to run and find his sister, and closes his eyes. Bob swallows the
Rat King. System: hidden trait BOSS EATER, skill Plague Bite, LV1 -> LV12, counter "bosses eaten 1/100".
Bob eats the gate. Rolf is telling the square Milo died when Milo climbs out with the Rat King's crown.
50 gold, Ash lives, Mom cooks meat, Pip names it "Bob Day". Cliffhanger: the System detects the next
boss 200 m away; a man in a red cloak (Guild Master Cassian) watches from a roof; "boss number two... found".

### Episode 2 (planned)
Weigh-in day: Bob cracks the Pet Stone (numbers go crazy, "???"), Cassian steps out of the crowd and
can see Bob's counter. Reveal who/what boss #2 is. Keep the same cast and style.

### How it is built (animation-studio plugin)
`slime-ep1/` is an animation-studio project (needs the plugin in the chat, Node 22+, ffmpeg, Chrome):
- `score.js`: the timeline (one shot per voice line, from `timeline.json`), subtitles, events
- `film.js`: every shot drawn in code (cast, Bob, Rat King, drake, backgrounds, UI overlays)
- `song.js`: the soundtrack (lofi village, dark sewer, orchestral reveal) + the narration `vo/NN.wav`
- render: `node song.js && node engine/render.js video && node engine/render.js mux`

For a new episode: write the lines, synthesize them with Speko in one call, transcribe with word
timestamps, cut into `vo/NN.wav` per line, build `timeline.json` (shot start = previous end, voice at
start + 0.2 s, shot length = max(1.4, voice + 0.32)), then write shots in `film.js`.

`legacy/` holds the older Python renderer (the user disliked that look; kept for reference).

### Plugins the user added
animation-studio (used), Anidoodle (not loaded in the old chat, try it in the new one as an
alternative style), audit-suite (not relevant).
