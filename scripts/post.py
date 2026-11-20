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


def prepare():
    s = load_state()
    posts = load_posts()
    if s["next"] >= len(posts):
        print("Zaloga objav je porabljena - dodaj nove vrstice v posts.txt")
        sys.exit(1)
    text = posts[s["next"]]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H%M")
    rel = f"images/{stamp}.jpg"
    render(text, os.path.join(ROOT, rel), seed=s["next"])
    rnd = random.Random(s["next"])
    caption = rnd.choice(CAPTIONS) + "\n.\n.\n" + " ".join(rnd.sample(HASHTAGS, 10))
    s["pending"] = {"index": s["next"], "image": rel, "caption": caption, "text": text}
    save_state(s)
    print("Pripravljeno:", text)


def _check(r):
    if r.status_code != 200:
        print("Napaka Instagram API:", r.status_code, r.text)
        sys.exit(1)
    return r.json()


def publish():
    token = os.environ["IG_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    s = load_state()
    p = s.get("pending")
    if not p:
        print("Ni pripravljene objave.")
        return
    image_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{p['image']}"

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
    {"prepare": prepare, "publish": publish, "refresh": refresh}[sys.argv[1]]()
