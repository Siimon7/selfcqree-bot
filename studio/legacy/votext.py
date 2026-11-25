import sys, importlib, re
for e in sys.argv[1:]:
    m = importlib.import_module(f"ep{e}")
    out = []
    for sc in m.SCENES:
        c = sc["cap"].replace("*", "").replace('"', "")
        c = re.sub(r"\bTeo\b", "Tay-oh", c); c = re.sub(r"\bSS\b", "S S", c); c = c.replace("READ", "Read").replace("FADING: 61%", "fading, sixty-one percent")
        out.append(c)
    print(f"=== {e}"); print("\\n\\n".join(out))
