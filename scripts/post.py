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


def prepare(kind="post"):
    cleanup()
    s = load_state()
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


def publish_buffer(p, image_url):
    """Objava prek Bufferja (Buffer ima svojo odobreno Meta aplikacijo)."""
    orgs = _buffer("query { account { organizations { id name } } }")["account"]["organizations"]
    channel = None
    for o in orgs:
        chans = _buffer('query { channels(input: {organizationId: %s}) { id name service } }'
                        % json.dumps(o["id"]))["channels"]
        for c in chans:
            if c["service"].lower() == "instagram" and "selfcqree" in (c["name"] or "").lower():
                channel = c
        if not channel:
            channel = next((c for c in chans if c["service"].lower() == "instagram"), None)
        if channel:
            break
    if not channel:
        fail("V Bufferju ni povezanega Instagram računa. Kanali:", orgs)

    due = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)).isoformat(timespec="seconds").replace("+00:00", "Z")
    res = _buffer("""
      mutation($input: CreatePostInput!) {
        createPost(input: $input) {
          ... on PostActionSuccess { post { id dueAt } }
          ... on MutationError { message }
        }
      }""", {"input": {
        "text": p["caption"], "channelId": channel["id"], "schedulingType": "automatic",
        "mode": "customScheduled", "dueAt": due,
        "assets": ([{"video": {"url": image_url}}] if p.get("kind") == "reel"
                   else [{"image": {"url": image_url, "metadata": {"altText": p["text"]}}}]),
        "metadata": {"instagram": {"type": "reel" if p.get("kind") == "reel" else "post",
                                   "shouldShareToFeed": True}},
    }})["createPost"]
    if "post" not in res:
        fail("Buffer ni sprejel objave:", res.get("message"))
    print("Poslano v Buffer za @%s, objava ob %s" % (channel["name"], res["post"]["dueAt"]))
    return res["post"]["id"]


def publish():
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    s = load_state()
    p = s.get("pending")
    if not p:
        print("Ni pripravljene objave.")
        return
    image_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{p['image']}"

    if os.environ.get("BUFFER_TOKEN"):
        mid = publish_buffer(p, image_url)
        s["history"].append({"index": p["index"], "buffer_id": mid,
                             "date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")})
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
