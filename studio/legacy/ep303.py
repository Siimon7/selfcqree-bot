EPNUM = 1
SERIES = "MY SLIME EATS BOSSES"
G = (120, 220, 120); GR = (150, 140, 150); RED_EYE = (230, 40, 40)
PURP = (170, 90, 230); GOLD = (255, 200, 60); RED = (255, 80, 80); GRN = (120, 230, 120); WHITE = (255, 255, 255)


def p(x, who="kid", **k): d = dict(k="p", x=x, who=who); d.update(k); return d
def sl(x, **k): d = dict(k="slime", x=x, size=42); d.update(k); return d
def bob(x, **k):
    d = dict(k="slime", x=x, col=GR, teeth=True, eye=RED_EYE, size=60); d.update(k); return d
def pt(x, kind, **k): d = dict(k="pet", x=x, kind=kind); d.update(k); return d
def rat(x, **k): d = dict(k="rat", x=x); d.update(k); return d
def S(bg, cap, *act, **k): d = dict(bg=bg, cap=cap, act=list(act)); d.update(k); return d

MILO = "milo"
SCENES = [
 # ================= ACT 1: the stakes
 S("square", "In seven days, every pet in Brindle gets weighed on the *Pet Stone*.", p(120, "girl"), pt(210, "wolf"), p(560, "hunter", face=-1), p(640, "kid", face=-1),
   fx=dict(label=("7 DAYS LEFT", RED))),
 S("square", "Over one hundred power, you get a guild *contract*.", fx=dict(board=("PET POWER", 0, 100, 0.2, 1.4, GRN, "OVER 100 = CONTRACT"))),
 S("square", "Under one hundred... the Guild takes your *pet*.", p(200, "noble"), pt(450, "hawk", face=-1), fx=dict(label=("UNDER 100 = TAKEN", RED), dark=0.25), heart=True),
 S("home", "For my family, a contract means *food*.", p(180, "mom", mood="sad"), p(330, "sis", h=150, mood="sad"), p(500, MILO, face=-1), fx=dict(pills=[("COINS: 3", 360, 200, GOLD, GOLD)])),
 S("home", "Because right now, we have *three coins*.", p(330, "sis", h=150, mood="sad"), fx=dict(ui=[("counter", "COINS", 3, 3, 0, 1)]), z=(1.25, 1.3), f=(330, 820)),
 S("square", "And my pet's power... is *two*.", p(170, MILO, mood="sad"), sl(470, mood="sad"), fx=dict(board=("PET POWER", 0, 2, 0.2, 0.6, RED, "SLIME · COMMON"))),
 S("village", "This is Bob. Bob is a *slime*.", p(250, MILO, mood="happy", arm="up"), sl(440, size=46, tag="BOB · LV 1", tagcol=(160, 220, 160)), z=(1.25, 1.32)),
 S("village", "The weakest pet in the whole *kingdom*.", sl(360, size=50, mood="sad", tag="ATK 1 · DEF 1"), fx=dict(pills=[("RANK: LAST", 360, 220, RED, RED)]), z=(1.3, 1.36)),
 S("village", "Tess got a wolf. Ash. Level *nine*.", p(250, "girl", mood="happy"), pt(440, "wolf", tag="ASH · LV 9", tagcol=GRN)),
 S("village", "Rolf, the mayor's son, got a *drake*.", p(250, "rich", mood="happy", arm="up"), pt(450, "drake", face=-1, tag="DRAKE · LV 15", tagcol=GOLD), beams=[(450, GOLD, 0.2)]),
 S("village", "I got... *Bob*.", p(250, MILO, mood="neutral"), sl(440, mood="happy"), hold=0.4),
 S("village", "Rolf laughed so hard he fell off the *fence*.", p(150, "rich", mood="laugh"), pt(280, "drake"), p(560, MILO, face=-1, mood="sad"), sl(440, mood="sad")),
 # ================= ACT 2: weird habit (played for laughs), failing
 S("home", "Bob has one *problem*.", sl(360, size=46), fx=dict(big=("?", 0.3, WHITE, 300, 110))),
 S("home", "He eats. *Everything*.", sl(360, size=52, mood="chomp", squash=0.15), fx=dict(big=("CHOMP!", 0.2)), boom=True),
 S("home", "My boots. My spoon. Half the *table*.", sl(360, size=(52, 60), mood="chomp", squash=0.12), p(560, "mom", face=-1, mood="angry"),
   fx=dict(dmg=[("-1 BOOT", 320, 600, 0.2), ("-1 SPOON", 400, 590, 0.9), ("-1/2 TABLE", 360, 570, 1.6)])),
 S("home", "Mom said if he eats the door, he's *soup*.", p(240, "mom", mood="angry", arm="point"), sl(450, mood="sad"), hold=0.3),
 S("cave", "So we trained. Every *day*.", p(200, MILO, mood="angry", arm="up"), sl(420), fx=dict(label=("DAY 1", WHITE))),
 S("cave", "Bob tried to bite a training *dummy*.", sl(330, mood="chomp", squash=0.2), fx=dict(dmg=[("MISS", 360, 600, 0.3)])),
 S("cave", "He bounced off. *Twice*.", sl(330, mood="sad", squash=0.3), fx=dict(dmg=[("MISS", 330, 600, 0.1), ("MISS", 400, 620, 0.8)])),
 S("cave", "Then he ate the *dummy*.", sl(360, size=(44, 56), mood="chomp", squash=0.15), fx=dict(big=("GULP.", 0.4, WHITE)), boom=True),
 S("cave", "Power still: *two*.", sl(360, size=56, mood="happy"), p(180, MILO, mood="sad"), fx=dict(board=("PET POWER", 2, 2, 0, 1, RED))),
 S("night", "But one night, I noticed something *weird*.", p(220, MILO, mood="neutral"), sl(430, size=50), fx=dict(dark=0.1), heart=True),
 S("night", "Bob swallowed an old rusty *sword*.", sl(380, size=52, mood="chomp", squash=0.15), fx=dict(dmg=[("-1 SWORD", 380, 600, 0.3)])),
 S("night", "And the sword never came *out*.", sl(380, size=56), p(180, MILO, mood="shock"), hold=0.3),
 S("night", "For a second, his eyes looked... *metal*.", sl(380, size=56, eye=(170, 180, 200)), fx=dict(dark=0.2), z=(1.35, 1.42), f=(380, 880), heart=True),
 S("night", "Then he burped. And it was *gone*.", sl(380, size=56, mood="happy"), fx=dict(big=("*BURP*", 0.3, WHITE, 300, 70))),
 # ================= quest
 S("square", "Two days before the weigh-in, the Guild posted a *bounty*.", fx=dict(board=("BOUNTY", 0, 50, 0.3, 1.2, GOLD, "GOLD · RAT KING"))),
 S("sewer", "The Rat King. Level twelve. Living right under our *streets*.", rat(420, size=0.85, tag="RAT KING · LV 12", tagcol=RED),
   fx=dict(big=("BOSS", 0.2, RED), shake=0.6), boom=True, z=(1.0, 1.05), f=(380, 790)),
 S("home", "Fifty gold. Enough to feed us for a *year*.", p(220, "mom"), p(360, "sis", h=150, mood="happy"), p(520, MILO, face=-1, mood="happy"), fx=dict(ui=[("counter", "COINS", 3, 53, 0.3, 1.6)])),
 S("square", "Rolf put a team together. His drake. Tess and *Ash*.", p(130, "rich", arm="up"), pt(240, "drake"), p(440, "girl"), pt(560, "wolf", face=-1)),
 S("square", "I asked to come. Rolf *grinned*.", p(200, "rich", mood="happy"), p(480, MILO, face=-1, mood="neutral"), sl(600, size=34)),
 S("square", "Sure. Every hunt needs *bait*.", p(200, "rich", mood="laugh", arm="point"), p(480, MILO, face=-1, mood="sad"), fx=dict(label=("ROLE: BAIT", RED))),
 S("home", "My sister gave me her lucky ribbon. Come back, she *said*.", p(280, "sis", h=150, mood="sad", arm="up"), p(440, MILO, face=-1, mood="happy"), z=(1.25, 1.3), heart=True),
 # ================= ACT 3: sewer, betrayal, crisis
 S("sewer", "The sewer smelled like a thousand dead *things*.", p(130, "rich"), pt(240, "drake"), p(380, "girl"), p(520, MILO, mood="sad"), sl(610, size=32), fx=dict(dark=0.2)),
 S("sewer", "I carried the torches. And the bags. And the *food*.", p(360, MILO, mood="sad", walk=1), fx=dict(dark=0.2, pills=[("WEIGHT: TOO MUCH", 360, 220, RED, RED)])),
 S("sewer", "Then the torches *flickered*.", p(360, MILO, mood="shock"), fx=dict(dark=0.45), heart=True, hold=0.4),
 S("sewer", "Something big was *breathing*.", fx=dict(dark=0.65, big=("...", 0.2, WHITE, 500, 90)), heart=True, hold=0.5),
 S("sewer", "The Rat King came out of the *dark*.", rat(440, size=1.0, tag="RAT KING · LV 12", tagcol=RED), fx=dict(shake=0.7, hp=("RAT KING · LV 12", 1.0), flash=True), boom=True, z=(1.0, 1.05), f=(380, 790)),
 S("sewer", "The drake's fire did *nothing*.", pt(180, "drake"), rat(470, size=0.85), beams=[(330, (255, 120, 40), 0.1)], fx=dict(hp=("RAT KING · LV 12", (1.0, 0.97)), dmg=[("-3", 470, 600, 0.4)])),
 S("sewer", "Ash jumped in front of Tess. And got *thrown*.", pt(200, "wolf", face=1), p(110, "girl", mood="shock"), rat(480, size=0.85),
   fx=dict(dmg=[("-80", 200, 640, 0.3)], shake=0.5, hp=("RAT KING · LV 12", 0.97)), boom=True),
 S("sewer", "Rolf screamed: *run*!", p(300, "rich", mood="shock", jit=3, arm="both"), fx=dict(big=("RUN!", 0.2, RED)), z=(1.25, 1.3)),
 S("sewer", "Everyone ran. I tried to *follow*.", p(150, "rich", x2=-100, face=-1, mood="shock"), p(250, "girl", x2=-60, face=-1, mood="shock"), p(500, MILO, x2=380, face=-1, mood="shock")),
 S("sewer", "Rolf turned around... and *pushed* me.", p(240, "rich", face=1, mood="angry", arm="point"), p(400, MILO, face=-1, mood="shock", jit=3), fx=dict(shake=0.4), boom=True),
 S("sewer", "Slow it down, bait, he *said*.", p(300, "rich", mood="happy", face=1), fx=dict(dark=0.2), z=(1.3, 1.36), f=(300, 760)),
 S("sewer", "Then they locked the *gate*.", p(360, MILO, mood="shock"), fx=dict(bars=True), boom=True),
 S("sewer", "I heard Tess crying on the other *side*.", p(360, MILO, mood="sad"), fx=dict(bars=True, dark=0.2), heart=True),
 S("sewer", "Just me. A slime. And a *boss*.", p(130, MILO, mood="sad", h=200), sl(250, size=36, mood="sad"), rat(520, size=0.9), fx=dict(dark=0.35, hp=("RAT KING · LV 12", 0.97)), heart=True, hold=0.4),
 S("sewer", "My torch started to *die*.", p(300, MILO, mood="sad"), fx=dict(dark=0.6), hold=0.3),
 S("sewer", "I pushed Bob behind me. Run, I *told* him.", p(330, MILO, mood="angry", arm="point", face=1), sl(200, size=36, mood="sad"), fx=dict(dark=0.4)),
 S("sewer", "If you get out... find my *sister*.", p(330, MILO, mood="sad"), sl(200, size=36, mood="sad"), fx=dict(dark=0.45), heart=True, hold=0.5),
 S("sewer", "The Rat King *opened* its mouth.", rat(430, size=1.1), fx=dict(dark=0.4, shake=0.5), boom=True, z=(1.1, 1.18), f=(300, 760)),
 S("sewer", "I closed my *eyes*.", fx=dict(dark=0.9), heart=True, hold=0.6),
 S("sewer", "Nothing *happened*.", fx=dict(dark=0.85), hold=0.4),
 S("sewer", "When I opened them, Bob was standing in *front* of me.", p(180, MILO, mood="shock"), sl(330, size=40), rat(560, size=0.95), fx=dict(dark=0.3)),
 S("sewer", "Bob didn't run. Bob never *runs*.", sl(330, size=44, mood="happy"), rat(560, size=0.95), fx=dict(dark=0.2), z=(1.25, 1.32), f=(360, 860)),
 S("sewer", "He *jumped*.", sl(330, size=54, mood="chomp", squash=0.3), rat(560, size=0.85), fx=dict(big=("!", 0.1, WHITE, 230, 120)), boom=True, z=(1.2, 1.3), f=(420, 820)),
 S("sewer", "And swallowed the Rat King. *Whole*.", sl(380, size=(50, 130), mood="chomp", squash=0.2), rat(470, size=0.8, to=0.35),
   fx=dict(shake=0.8, flash=True, big=("GULP.", 0.4), hp=("RAT KING · LV 12", (0.97, 0.0))), boom=True, z=(1.0, 1.05), f=(380, 790)),
 S("sewer", "*Silence*.", sl(380, size=110, mood="sad"), p(130, MILO, mood="shock", h=200), fx=dict(dark=0.35), heart=True, hold=0.7, z=(1.0, 1.04), f=(360, 790)),
 # ================= the reveal
 S("dark", "Then a voice spoke. Not Bob's. The *System's*.", fx=dict(ui=[("window", "SYSTEM", ["HIDDEN TRAIT UNLOCKED"], 0.3)]), boom=True),
 S("dark", "Hidden trait: *Boss Eater*.", sl(360, size=70), beams=[(360, PURP, 0.1)], fx=dict(ui=[("item", "BOSS EATER", "MYTHIC TRAIT", "absorbs what it eats", 0.3)]), boom=True),
 S("dark", "Everything Bob ate... he *kept*.", sl(360, size=70), fx=dict(dmg=[("BOOT", 250, 600, 0.1), ("SWORD", 470, 580, 0.5), ("DUMMY", 360, 560, 0.9)])),
 S("dark", "He was just waiting for something *strong* enough.", sl(360, size=70), heart=True),
 S("sewer", "Bob turned gray. His eyes went red. And he grew *teeth*.", bob(380, size=90, mood="happy"), fx=dict(flash=True), z=(1.12, 1.2), boom=True),
 S("cave", "Slime has absorbed: *Rat King*.", bob(360, size=75), fx=dict(ui=[("window", "SYSTEM", ["ABSORBED: RAT KING", "SKILL: PLAGUE BITE (EPIC)"], 0.1)])),
 S("cave", "Level one... to level *twelve*.", bob(360, size=80, tag="BOB · LV 12", tagcol=GOLD), beams=[(360, GOLD, 0.0)], fx=dict(big=("+11 LEVELS", 0.4, GOLD), ui=[("counter", "LEVEL", 1, 12, 0.2, 1.6)])),
 S("dark", "And above his head, a counter *appeared*.", bob(360, size=70), fx=dict(dark=0.1), heart=True),
 S("dark", "Bosses eaten: one... of one *hundred*.", bob(360, size=70), fx=dict(big=("1 / 100", 0.4, WHITE, 400, 120)), boom=True),
 # ================= ACT 4: payoff
 S("sewer", "Bob ate the gate *too*.", bob(360, size=70, mood="chomp"), fx=dict(bars=True, flash=True, shake=0.5, big=("CRUNCH", 0.2, WHITE)), boom=True),
 S("square", "Up in the square, Rolf was telling everyone I *died*.", p(200, "rich", mood="sad", arm="up"), p(400, "kid"), p(520, "hunter"), p(620, "mom", face=-1, mood="sad")),
 S("square", "That I was brave. That he tried to save *me*.", p(250, "rich", mood="sad", arm="both"), p(560, "girl", face=-1, mood="angry")),
 S("square", "Then the sewer lid *moved*.", p(200, "rich", mood="shock"), p(520, "hunter", face=-1, mood="shock"), fx=dict(shake=0.4), boom=True),
 S("square", "I climbed out. Holding the Rat King's *crown*.", p(360, MILO, mood="neutral", arm="up"), bob(500, size=50), beams=[(330, GOLD, 0.3)], z=(1.2, 1.28)),
 S("square", "Nobody *spoke*.", p(110, "rich", mood="shock"), p(220, "kid", mood="shock"), p(560, "hunter", face=-1, mood="shock"), p(650, "mom", face=-1, mood="shock"), hold=0.6),
 S("square", "Rolf's drake hid behind *him*.", p(250, "rich", mood="shock", jit=2), pt(170, "drake"), bob(500, size=55, mood="happy")),
 S("square", "The Guild paid me fifty *gold*.", p(300, MILO, mood="happy", arm="both"), bob(480, size=50), beams=[(300, GOLD, 0.2)], fx=dict(ui=[("counter", "COINS", 3, 53, 0.2, 1.4)]), boom=True),
 S("village", "Tess ran out and hugged Bob. Ash was going to *live*.", p(300, "girl", mood="happy"), bob(420, size=48, mood="happy"), pt(560, "wolf", face=-1), heart=True),
 S("home", "That night, Mom cooked meat. For the first time in a *year*.", p(190, "mom", mood="happy"), p(320, "sis", h=150, mood="laugh"), p(460, MILO, face=-1, mood="happy"), bob(600, size=38)),
 S("home", "My sister named it *Bob Day*.", p(330, "sis", h=150, mood="laugh", arm="both"), bob(480, size=44, mood="happy"), z=(1.3, 1.36), f=(380, 860)),
 # ================= cliffhanger
 S("night", "But after everyone was asleep... the counter *glowed*.", bob(360, size=60, tag="1 / 100", tagcol=GOLD), beams=[(360, RED, 0.5)], heart=True),
 S("night", "A new line *appeared*.", bob(360, size=60), fx=dict(ui=[("window", "SYSTEM", ["NEXT BOSS DETECTED", "DISTANCE: 200 M"], 0.2)]), boom=True),
 S("night", "Two hundred meters. That's the middle of the *village*.", p(250, MILO, mood="shock"), bob(450, size=50), fx=dict(dark=0.2)),
 S("night", "I looked out the window. Someone on the roof was *watching* us.", p(500, "noble", h=200, face=-1), fx=dict(dark=0.35), z=(1.2, 1.3), f=(500, 760), heart=True),
 S("night", "A man in a red *cloak*.", p(400, "noble", h=260, face=-1, mood="happy"), fx=dict(dark=0.3), z=(1.25, 1.35), f=(400, 740)),
 S("dark", "And Bob's counter said: boss number two... *found*.", fx=dict(big=("BOSS 2 / 100", 0.2, RED, 380, 76)), boom=True, hold=1.0),
]
