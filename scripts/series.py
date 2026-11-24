"""
Zgodbe (Red Ink Episodes): vsak dan objavi naslednjo epizodo iz series/queue.json
na nov Instagram profil (Reel) in YouTube (Short) prek Bufferja.

  python scripts/series.py publish   -> objavi naslednjo epizodo
  python scripts/series.py status    -> izpiše, katera epizoda je na vrsti

Nove serije: videe daj v series/<ime>/ in jih dodaj na konec series/queue.json.
"""
import json, os, sys, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post import _buffer, _buffer_soft, _channels, CREATE, fail, warn, ROOT

QUEUE = os.path.join(ROOT, "series", "queue.json")
STATE = os.path.join(ROOT, "series", "state.json")

HASHTAGS = "#animation #story #litrpg #fantasy #storytime #webnovel #shorts"


def load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def save_state(s):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)


def pick_channels(chans):
    """Instagram, ki NI @selfcqree (ali ime iz SERIES_IG), in YouTube kanal."""
    want = (os.environ.get("SERIES_IG") or "").lower().lstrip("@")
    igs = [c for c in chans if c["service"].lower() == "instagram"]
    if want:
        ig = next((c for c in igs if want in (c["name"] or "").lower()), None)
    else:
        ig = next((c for c in igs if "selfcqree" not in (c["name"] or "").lower()), None)
    yt = next((c for c in chans if c["service"].lower() == "youtube"), None)
    return ig, yt


def publish():
    queue = load(QUEUE, [])
    s = load(STATE, {"next": 0, "history": []})
    i = s["next"]
    if i >= len(queue):
        print("Vse epizode so objavljene. Dodaj novo serijo v series/queue.json.")
        return
    ep = queue[i]
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{ep['file']}"

    ig, yt = pick_channels(_channels())
    if not ig and not yt:
        fail("V Bufferju ni novega Instagram ali YouTube kanala za zgodbe.")

    due = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)).isoformat(timespec="seconds").replace("+00:00", "Z")
    base = {"schedulingType": "automatic", "mode": "customScheduled", "dueAt": due, "assets": [{"video": {"url": url}}]}
    caption = f"{ep['hook']}\n\n{ep['title']}\n{ep['question']} 👇\nFollow so you don't miss the next episode.\n.\n.\n{HASHTAGS}"
    done = {}

    if ig:
        res = _buffer(CREATE, {"input": dict(base, channelId=ig["id"], text=caption,
                                             metadata={"instagram": {"type": "reel", "shouldShareToFeed": True}})})["createPost"]
        if "post" not in res:
            fail("Buffer ni sprejel Reela:", res.get("message"))
        done["instagram"] = res["post"]["id"]
        print(f"Instagram {ig['name']}: {ep['title']} ob {res['post']['dueAt']}")

    if yt:
        desc = f"{ep['hook']}\n\n{ep['question']}\nNew episode every day.\n\n{HASHTAGS}"
        data, err = _buffer_soft(CREATE, {"input": dict(base, channelId=yt["id"], text=desc,
                                                        metadata={"youtube": {"title": ep["title"][:100], "categoryId": "1",
                                                                              "madeForKids": False}})})
        r = (data or {}).get("createPost") or {}
        if err or "post" not in r:
            warn("YouTube: objava ni uspela:", err or r.get("message"))
        else:
            done["youtube"] = r["post"]["id"]
            print(f"YouTube {yt['name']}: {ep['title']} ob {r['post']['dueAt']}")

    s["history"].append({"index": i, "title": ep["title"], "buffer": done,
                         "date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")})
    s["next"] = i + 1
    save_state(s)


def status():
    queue = load(QUEUE, [])
    s = load(STATE, {"next": 0})
    print(f"Na vrsti: {s['next'] + 1} / {len(queue)}")


if __name__ == "__main__":
    {"publish": publish, "status": status}[sys.argv[1] if len(sys.argv) > 1 else "status"]()
