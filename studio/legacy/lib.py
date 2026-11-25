from render import GY, RED
def _a(k, x, h, **kw):
    d = dict(k=k, x=x, h=h); d.update(kw); return d
def kai(x, h=200, **kw): return _a("kai", x, h, **kw)
def wr(x, h=420, **kw): return _a("wraith", x, h, **kw)
def mira(x, h=220, **kw): return _a("mira", x, h, **kw)
def osk(x, h=260, **kw): return _a("osk", x, h, **kw)
def nell(x, h=155, **kw): return _a("nell", x, h, **kw)
def mom(x, h=200, **kw): return _a("mom", x, h, **kw)
def var(x, h=270, **kw): return _a("varrow", x, h, face=kw.pop("face", -1), **kw)
def brenn(x, h=250, **kw): return _a("brenn", x, h, **kw)
def guard(x, h=235, **kw): return _a("guard", x, h, **kw)
def kid(x, h=115, **kw): return _a("kid", x, h, **kw)
def fig(x, h=230, **kw): return _a("fig", x, h, **kw)
def S(bg, cap, *acts, **kw):
    d = dict(bg=bg, cap=cap, act=list(acts), z=(1.02, 1.08), f=(360, 620)); d.update(kw); return d
def crowd(xs, **kw): return [kid(x, 110 + (i % 3) * 10, ph=i, col=(52, 48, 46, 255), face=1 if x < 360 else -1, **kw) for i, x in enumerate(xs)]
U = ("UNRANKED", "LV 0", True, False)
B = ("???", "MASTER", False, True)
WB = ("WRAITH", "BOUND", False, True)
VT = ("LORD VARROW", "RANK S", False, True)
GT = ("HOUSE VARROW", "RANK C", False, False)
BR = ("CPT. BRENN", "RANK B", False, False)
CARVE = (205, 196, 180, 255)
STAGE = dict(stone=1.0, stonex=480, stoneb=GY - 70)
def BLV(lv): return ("???", f"MASTER · LV {lv}", False, True)
