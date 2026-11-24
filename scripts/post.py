"""
Samodejno objavljanje na @selfcqree prek uradnega Instagram API-ja.

  python scripts/post.py prepare   -> izbere naslednjo objavo in ustvari sliko
  python scripts/post.py publish   -> objavi pripravljeno sliko na Instagram
  python scripts/post.py refresh   -> podaljša token (velja 60 dni)
"""
import json, os, random, sys, time, datetime
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import render
from reel import render_reel
from carousel import render_carousel
from story import render_story
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state.json")
API = "https://graph.instagram.com/v23.0"

CAPTIONS = [
    "tag someone who needs to see this ◡̈",
    "be honest… is it just me? 🫠",
    "send this to your bestie 💌",
    "relatable or nah? ⬇️",
    "this is so me it hurts",
    "save this for later ♡",
    "comment 🙋 if this is you",
    "follow @selfcqree for more ◡̈",
]
HASHTAGS = [
    "#relatable", "#relatablequotes", "#relatablememes", "#mood", "#selfcare",
    "#overthinking", "#quotes", "#tweets", "#relatabletweets", "#feelings",
    "#mentalhealth", "#reminder", "#genz", "#funnytweets", "#lifequotes",
]


def fail(*msg):
    text = " ".join(str(m) for m in msg)
    print(text)
    with open(os.path.join(ROOT, "last_error.txt"), "w") as f:
        f.write(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes") + "  " + text + "\n")
    sys.exit(1)


def load_state():
    if os.path.exists(STATE):
        with open(STATE) as f:
            return json.load(f)
    return {"next": 0, "pending": None, "history": []}


def save_state(s):
    with open(STATE, "w") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)


def load_posts():
    with open(os.path.join(ROOT, "posts.txt"), encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def cleanup(days=5):
    """Pobriše stare slike/videe (objavljene so že), da repozitorij ne raste."""
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
    for f in glob.glob(os.path.join(ROOT, "images", "*.jpg")) + glob.glob(os.path.join(ROOT, "videos", "*.mp4")):
        try:
            stamp = datetime.datetime.strptime(os.path.basename(f)[:15], "%Y-%m-%d_%H%M").replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            continue
        if stamp < cutoff:
            os.remove(f)


def prepare_carousel(s, stamp):
    items = json.load(open(os.path.join(ROOT, "carousels.json"), encoding="utf-8"))
    i = s.get("carousel_next", 0) % len(items)
    item = items[i]
    paths = render_carousel(item, os.path.join(ROOT, "images", f"{stamp}_c"), seed=i, shop_live=bool(os.environ.get("SHOP_URL")))
    rel = [os.path.relpath(x, ROOT) for x in paths]
    rnd = random.Random(1000 + i)
    caption = item["caption"] + "\n.\n.\n" + " ".join(rnd.sample(HASHTAGS, 10))
    s["pending"] = {"index": None, "carousel": i, "image": rel[0], "images": rel, "kind": "carousel",
                    "caption": caption, "text": item["title"]}
    s["carousel_next"] = i + 1
    save_state(s)
    print("Pripravljen carousel:", item["title"])


def prepare_story(s, stamp):
    items = json.load(open(os.path.join(ROOT, "stories.json"), encoding="utf-8"))
    i = s.get("story_next", 0) % len(items)
    rel = f"images/{stamp}_story.jpg"
    render_story(items[i], os.path.join(ROOT, rel), seed=i)
    s["pending"] = {"index": None, "story": i, "image": rel, "kind": "story", "caption": items[i]["q"], "text": items[i]["q"]}
    s["story_next"] = i + 1
    save_state(s)
    print("Pripravljen story:", items[i]["q"])


def prepare(kind="post"):
    cleanup()
    s = load_state()
    now = datetime.datetime.now(datetime.timezone.utc)
    if kind == "story":
        return prepare_story(s, now.strftime("%Y-%m-%d_%H%M"))
    if kind == "carousel" or (kind == "post" and now.weekday() == 6):  # nedelja popoldne = carousel
        return prepare_carousel(s, now.strftime("%Y-%m-%d_%H%M"))
    posts = load_posts()
    if s["next"] >= len(posts):
        print("Zaloga objav je porabljena - dodaj nove vrstice v posts.txt")
        sys.exit(1)
    text = posts[s["next"]]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H%M")
    if kind == "reel":
        os.makedirs(os.path.join(ROOT, "videos"), exist_ok=True)
        rel = f"videos/{stamp}.mp4"
        render_reel(text, os.path.join(ROOT, rel), seed=s["next"])
    else:
        rel = f"images/{stamp}.jpg"
        render(text, os.path.join(ROOT, rel), seed=s["next"])
    rnd = random.Random(s["next"])
    caption = rnd.choice(CAPTIONS) + "\n.\n.\n" + " ".join(rnd.sample(HASHTAGS, 10))
    s["pending"] = {"index": s["next"], "image": rel, "kind": kind, "caption": caption, "text": text}
    save_state(s)
    print("Pripravljeno:", text)


def _check(r):
    if r.status_code != 200:
        fail("Napaka Instagram API:", r.status_code, r.text)
    return r.json()


BUFFER_API = "https://api.buffer.com"


def _buffer(query, variables=None):
    r = requests.post(BUFFER_API, json={"query": query, "variables": variables or {}},
                      headers={"Authorization": "Bearer " + os.environ["BUFFER_TOKEN"]}, timeout=60)
    try:
        j = r.json()
    except Exception:
        fail("Buffer ni vrnil JSON:", r.status_code, r.text[:500])
    if r.status_code != 200 or j.get("errors"):
        fail("Napaka Buffer API:", r.status_code, j)
    return j["data"]


def warn(*msg):
    """Napaka na dodatnem kanalu (TikTok/Pinterest) - zabeleži, a ne ustavi objave na Instagramu."""
    text = " ".join(str(m) for m in msg)
    print("OPOZORILO:", text)
    with open(os.path.join(ROOT, "last_error.txt"), "a") as f:
        f.write(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes") + "  OPOZORILO " + text + "\n")


def _buffer_soft(query, variables=None):
    r = requests.post(BUFFER_API, json={"query": query, "variables": variables or {}},
                      headers={"Authorization": "Bearer " + os.environ["BUFFER_TOKEN"]}, timeout=60)
    try:
        j = r.json()
    except Exception:
        return None, f"{r.status_code} {r.text[:300]}"
    if r.status_code != 200 or j.get("errors"):
        return None, j
    return j["data"], None


CREATE = """
  mutation($input: CreatePostInput!) {
    createPost(input: $input) {
      ... on PostActionSuccess { post { id dueAt } }
      ... on MutationError { message }
    }
  }"""


def _channels():
    orgs = _buffer("query { account { organizations { id name } } }")["account"]["organizations"]
    out = []
    for o in orgs:
        out += _buffer('query { channels(input: {organizationId: %s}) { id name service } }' % json.dumps(o["id"]))["channels"]
    return out


def _pinterest_board(channel_id):
    if os.environ.get("PINTEREST_BOARD"):
        return os.environ["PINTEREST_BOARD"]
    data, err = _buffer_soft('query { channel(input: {id: %s}) { metadata { ... on PinterestMetadata { boards { serviceId name } } } } }' % json.dumps(channel_id))
    if err or not data:
        warn("Pinterest: ne najdem tabel (boards):", err)
        return None
    boards = ((data.get("channel") or {}).get("metadata") or {}).get("boards") or []
    pick = next((b for b in boards if "selfcqree" in b["name"].lower() or "self" in b["name"].lower()), boards[0] if boards else None)
    return pick["serviceId"] if pick else None


def publish_buffer(p, urls):
    """Instagram (obvezno) + TikTok za Reels + Pinterest za slike, če sta povezana v Bufferju."""
    chans = _channels()
    ig = next((c for c in chans if c["service"].lower() == "instagram" and "selfcqree" in (c["name"] or "").lower()), None) \
        or next((c for c in chans if c["service"].lower() == "instagram"), None)
    if not ig:
        fail("V Bufferju ni povezanega Instagram računa. Kanali:", chans)
    kind = p.get("kind", "post")
    due = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)).isoformat(timespec="seconds").replace("+00:00", "Z")
    if kind == "reel":
        assets = [{"video": {"url": urls[0]}}]
    else:
        assets = [{"image": {"url": u, "metadata": {"altText": p["text"][:200]}}} for u in urls]
    base = {"text": p["caption"], "schedulingType": "automatic", "mode": "customScheduled", "dueAt": due, "assets": assets}

    ig_meta = {"type": "story", "shouldShareToFeed": False} if kind == "story" else {"type": "reel" if kind == "reel" else "post", "shouldShareToFeed": True}
    res = _buffer(CREATE, {"input": dict(base, channelId=ig["id"], metadata={"instagram": ig_meta})})["createPost"]
    if "post" not in res:
        fail("Buffer ni sprejel objave:", res.get("message"))
    print("Instagram @%s: objava ob %s" % (ig["name"], res["post"]["dueAt"]))

    for c in chans:
        svc = c["service"].lower()
        if kind == "story":
            continue
        if svc == "tiktok" and kind == "reel":
            inp = dict(base, channelId=c["id"], text=p["caption"][:2000])
        elif svc == "pinterest" and kind != "reel":
            board = _pinterest_board(c["id"])
            if not board:
                continue
            shop = os.environ.get("SHOP_URL") or "https://www.instagram.com/selfcqree/"
            inp = dict(base, channelId=c["id"], assets=assets[:1],
                       text=p["text"] + "\n\nmore gentle, relatable reminders from @selfcqree ♡",
                       metadata={"pinterest": {"boardServiceId": board, "title": p["text"][:95], "url": shop}})
        else:
            continue
        data, err = _buffer_soft(CREATE, {"input": inp})
        r2 = (data or {}).get("createPost") or {}
        if err or "post" not in r2:
            warn(f"{svc}: objava ni uspela:", err or r2.get("message"))
        else:
            print(f"{svc} {c['name']}: objava ob {r2['post']['dueAt']}")
    return res["post"]["id"]


def publish():
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    s = load_state()
    p = s.get("pending")
    if not p:
        print("Ni pripravljene objave.")
        return
    base_url = f"https://raw.githubusercontent.com/{repo}/{branch}/"
    image_url = base_url + p["image"]
    urls = [base_url + x for x in p.get("images", [p["image"]])]

    if os.environ.get("BUFFER_TOKEN"):
        mid = publish_buffer(p, urls)
        s["history"].append({"index": p["index"], "kind": p.get("kind"), "buffer_id": mid,
                             "date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")})
        if p.get("kind") not in ("carousel", "story"):
            s["next"] = p["index"] + 1
        s["pending"] = None
        save_state(s)
        return

    token = os.environ["IG_TOKEN"]

    me = _check(requests.get(f"{API}/me", params={"fields": "user_id,username", "access_token": token}))
    uid = me["user_id"]

    c = _check(requests.post(f"{API}/{uid}/media", data={
        "image_url": image_url, "caption": p["caption"], "access_token": token}))
    cid = c["id"]

    for _ in range(20):
        st = _check(requests.get(f"{API}/{cid}", params={"fields": "status_code", "access_token": token}))
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            print("Instagram ni sprejel slike:", st)
            sys.exit(1)
        time.sleep(5)

    res = _check(requests.post(f"{API}/{uid}/media_publish", data={"creation_id": cid, "access_token": token}))
    print("Objavljeno na @%s, id %s" % (me.get("username"), res["id"]))

    s["history"].append({"index": p["index"], "media_id": res["id"],
                         "date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")})
    s["next"] = p["index"] + 1
    s["pending"] = None
    save_state(s)


def refresh():
    token = os.environ["IG_TOKEN"]
    r = _check(requests.get("https://graph.instagram.com/refresh_access_token",
                            params={"grant_type": "ig_refresh_token", "access_token": token}))
    new = r["access_token"]
    print("::add-mask::" + new)  # skrije token v GitHub logih
    with open("/tmp/new_token.txt", "w") as f:
        f.write(new)
    print("Token podaljšan za %d dni" % (r.get("expires_in", 0) // 86400))


if __name__ == "__main__":
    if sys.argv[1] == "prepare":
        prepare(sys.argv[2] if len(sys.argv) > 2 else "post")
    else:
        {"publish": publish, "refresh": refresh}[sys.argv[1]]()
