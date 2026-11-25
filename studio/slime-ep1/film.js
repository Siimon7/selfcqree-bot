// MY SLIME EATS BOSSES - EP 1 (9:16). One shot per voiceover line; every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, Ch = globalThis.Ch, Subs = globalThis.Subs, Shots = globalThis.Shots, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H, SAFE = G.SAFE;
  const FEET = 1230, CAPY = 1400;
  const INK = '#2A2320';

  // ---------------- cast ----------------
  const CAST = {
    milo: { outfit: 'tee', shirt: '#9C7B57', trim: '#7A5E40', bottoms: 'pants', shorts: '#4D4038', skin: '#EDBE95', hair: '#5A3A22', hairStyle: 'short', shoes: '#3A2A22', freckles: true },
    tess: { outfit: 'tee', shirt: '#4F9A6B', bottoms: 'pants', shorts: '#5B4A3A', skin: '#F0C9A5', hair: '#D9A441', hairStyle: 'ponytail', shoes: '#3A2A22' },
    rolf: { outfit: 'shirt', shirt: '#E8B84A', collar: '#FFF4D6', bottoms: 'pants', shorts: '#7A2E2E', skin: '#F3D0B0', hair: '#F2D27A', hairStyle: 'quiff', shoes: '#5A2A1A', build: 'broad' },
    mom: { outfit: 'dress', shirt: '#8C6A9E', skin: '#EDBE95', hair: '#6B4226', hairStyle: 'bun', shoes: '#3A2A22' },
    pip: { outfit: 'dress', shirt: '#E8829A', skin: '#F0C9A5', hair: '#6B4226', hairStyle: 'ponytail', shoes: '#3A2A22' },
    brann: { outfit: 'tee', shirt: '#6E7F4E', bottoms: 'pants', shorts: '#3F3A34', skin: '#C98A62', hair: '#2A2320', hairStyle: 'buzz', facialHair: 'beard', build: 'broad' },
    kid: { outfit: 'hoodie', shirt: '#5B7DB1', bottoms: 'pants', shorts: '#3F3A34', skin: '#D59B72', hair: '#2A2320', hairStyle: 'curlytop' },
    guild: { outfit: 'suit', robe: '#3B2E4A', trim: '#C23B3B', shirt: '#F6F0E2', skin: '#E9C2A0', hair: '#B9B9C2', hairStyle: 'short', facialHair: 'trimmed', build: 'regular' },
    cassian: { outfit: 'suit', robe: '#221B2C', trim: '#B32630', shirt: '#E8E2D4', skin: '#E9D2BE', hair: '#E6E6EC', hairStyle: 'short', facialHair: 'trimmed', build: 'slim' },
  };
  globalThis.CAST = CAST;

  const MOOD = {
    neutral: { eyes: 'normal', brows: 'neutral', mouth: 'flat' },
    happy: { eyes: 'happy', brows: 'up', mouth: 'smile' },
    laugh: { eyes: 'happy', brows: 'up', mouth: 'grin' },
    shock: { eyes: 'wide', brows: 'up', mouth: 'o' },
    sad: { eyes: 'normal', brows: 'worried', mouth: 'wavy' },
    angry: { eyes: 'normal', brows: 'determined', mouth: 'flat' },
    scared: { eyes: 'wide', brows: 'worried', mouth: 'open' },
    smirk: { eyes: 'normal', brows: 'neutral', mouth: 'smirk' },
    brave: { eyes: 'normal', brows: 'determined', mouth: 'smile' },
  };

  // ---------------- props & creatures ----------------
  // Bob: a jelly blob. o = { x, y, r, col, mood: happy|sad|chomp|wide|metal, teeth, eyeCol, squash, t }
  function bob(ctx, o) {
    const { x, y = FEET, r = 70, col = '#7BD36B', mood = 'happy', teeth = false, eyeCol = INK, t = G.t, seed = 2000, glow = 0 } = o;
    const wob = Math.sin(t * 4.2) * 0.05 + (o.squash || 0);
    const rx = r * (1.18 + wob), ry = r * (0.86 - wob);
    const cy = y - ry;
    ctx.save();
    ctx.fillStyle = 'rgba(20,10,20,0.22)'; ctx.beginPath(); ctx.ellipse(x, y + 4, rx * 0.95, r * 0.16, 0, 0, Math.PI * 2); ctx.fill();
    if (glow > 0) { const g = ctx.createRadialGradient(x, cy, r * 0.2, x, cy, r * 2.6); g.addColorStop(0, `rgba(200,120,255,${0.55 * glow})`); g.addColorStop(1, 'rgba(200,120,255,0)'); ctx.fillStyle = g; ctx.fillRect(x - r * 3, cy - r * 3, r * 6, r * 6); }
    const pts = []; for (let i = 0; i < 28; i++) { const a = (i / 28) * Math.PI * 2; const flat = Math.sin(a) > 0.55 ? 0.82 : 1; pts.push([x + Math.cos(a) * rx, cy + Math.sin(a) * ry * flat + (Math.sin(a) > 0 ? r * 0.06 : 0)]); }
    G.shape(ctx, pts, { fill: col, lw: Math.max(4, r * 0.07), seed, hatch: { color: 'rgba(0,0,0,0.08)', gap: 9, angle: -0.6 } });
    G.ellipse(ctx, x - rx * 0.42, cy - ry * 0.45, rx * 0.2, ry * 0.14, { fill: 'rgba(255,255,255,0.75)', lw: 0, seed: seed + 1, amp: 0.3 });
    const ey = cy - ry * 0.08, er = r * 0.2;
    for (const sd of [-1, 1]) {
      const ex = x + sd * rx * 0.33;
      if (mood === 'happy' && Math.floor(t * 0.7 + seed) % 5 !== 9) {
        G.ellipse(ctx, ex, ey, er, er * 1.2, { fill: '#FFFFFF', lw: 3.5, seed: seed + 2 + sd });
        ctx.fillStyle = eyeCol; ctx.beginPath(); ctx.ellipse(ex + sd * 2, ey + er * 0.2, er * 0.5, er * 0.62, 0, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#FFF'; ctx.beginPath(); ctx.arc(ex - er * 0.15, ey - er * 0.1, er * 0.18, 0, Math.PI * 2); ctx.fill();
      } else if (mood === 'sad') {
        G.ellipse(ctx, ex, ey, er, er * 1.1, { fill: '#FFFFFF', lw: 3.5, seed: seed + 2 + sd });
        ctx.fillStyle = eyeCol; ctx.beginPath(); ctx.ellipse(ex, ey + er * 0.35, er * 0.45, er * 0.5, 0, 0, Math.PI * 2); ctx.fill();
        G.line(ctx, [[ex - er, ey - er * 1.1 - sd * er * 0.4], [ex + er, ey - er * 1.1 + sd * er * 0.4]], { lw: 4, seed: seed + 5 + sd });
      } else if (mood === 'wide' || mood === 'metal' || mood === 'chomp') {
        G.ellipse(ctx, ex, ey, er * 1.15, er * 1.35, { fill: mood === 'metal' ? '#C9D2DE' : '#FFFFFF', lw: 3.5, seed: seed + 2 + sd });
        ctx.fillStyle = mood === 'metal' ? '#5E6B7C' : eyeCol; ctx.beginPath(); ctx.arc(ex, ey, er * 0.38, 0, Math.PI * 2); ctx.fill();
        if (mood === 'metal') { ctx.fillStyle = '#FFF'; ctx.fillRect(ex - er * 0.5, ey - er * 0.7, er * 0.25, er * 0.9); }
      } else {
        ctx.fillStyle = eyeCol; ctx.beginPath(); ctx.ellipse(ex, ey, er * 0.55, er * 0.7, 0, 0, Math.PI * 2); ctx.fill();
      }
    }
    const my = cy + ry * 0.38;
    if (mood === 'chomp') {
      G.ellipse(ctx, x, my, rx * 0.55, ry * 0.36, { fill: '#4A1E2A', lw: 4, seed: seed + 8 });
      G.ellipse(ctx, x, my + ry * 0.14, rx * 0.3, ry * 0.12, { fill: '#E8718D', lw: 0, seed: seed + 9 });
    } else if (mood === 'sad') G.line(ctx, [[x - r * 0.2, my + 6], [x, my - 2], [x + r * 0.2, my + 6]], { lw: 4, seed: seed + 8 });
    else if (mood === 'wide' || mood === 'metal') G.ellipse(ctx, x, my, r * 0.1, r * 0.12, { fill: '#4A1E2A', lw: 3, seed: seed + 8 });
    else G.line(ctx, [[x - r * 0.22, my - 4], [x - r * 0.08, my + 6], [x + r * 0.08, my + 6], [x + r * 0.22, my - 4]], { lw: 4, seed: seed + 8 });
    if (teeth) {
      const tw = r * 0.14;
      for (let k = -2; k <= 2; k++) G.poly(ctx, [[x + k * tw * 1.15 - tw / 2, my - 2], [x + k * tw * 1.15 + tw / 2, my - 2], [x + k * tw * 1.15, my + tw * 1.3]], { fill: '#FFFDF4', lw: 2.5, seed: seed + 20 + k, step: 6 });
    }
    ctx.restore();
    return cy - ry;
  }
  const BOBG = '#7BD36B', BOBGRAY = '#9A93A3', REDEYE = '#D8282E';
  function bob2(ctx, o) { return bob(ctx, { col: BOBGRAY, teeth: true, eyeCol: REDEYE, ...o }); }

  // the Rat King
  function rat(ctx, o) {
    const { x, y = FEET, s = 1, t = G.t, seed = 2100, face = -1, mouth = 0, alpha = 1 } = o;
    ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, y); ctx.scale(s * -face * -1, s);
    ctx.fillStyle = 'rgba(20,10,20,0.25)'; ctx.beginPath(); ctx.ellipse(0, 4, 260, 26, 0, 0, Math.PI * 2); ctx.fill();
    const br = Math.sin(t * 2.4) * 6;
    G.line(ctx, [[-200, -90], [-300, -60], [-380, -110], [-430, -60]], { color: '#C98F9A', lw: 22, seed: seed + 1, step: 20 });
    for (const lx of [-150, -70, 60, 140]) G.limb(ctx, [[lx, -70], [lx + 10, -6]], { color: '#6F6873', lw: 34, seed: seed + 2 + lx });
    G.ellipse(ctx, 0, -170 - br, 230, 140 + br, { fill: '#7D7682', lw: 6, seed: seed + 5, hatch: { color: 'rgba(30,20,40,0.22)', gap: 8, angle: 0.7 } });
    // head (to the right in local space)
    ctx.save(); ctx.translate(210, -200 - br); ctx.rotate(-0.1 + mouth * 0.25);
    for (const sd of [0, 1]) G.ellipse(ctx, -30 + sd * 50, -110, 52, 62, { fill: '#C98F9A', lw: 5, seed: seed + 8 + sd });
    G.poly(ctx, [[-70, -80], [60, -70], [210, 10], [60, 70], [-70, 60]], { fill: '#8A838F', lw: 6, seed: seed + 10, step: 22 });
    G.ellipse(ctx, 205, 8, 18, 16, { fill: '#3A1D22', lw: 3, seed: seed + 11 });
    G.ellipse(ctx, 40, -22, 20, 18, { fill: '#FFDDDD', lw: 3.5, seed: seed + 12 });
    ctx.fillStyle = '#D8282E'; ctx.beginPath(); ctx.arc(44, -20, 10, 0, Math.PI * 2); ctx.fill();
    G.line(ctx, [[10, -52], [70, -38]], { lw: 6, seed: seed + 13 });
    if (mouth > 0.05) G.poly(ctx, [[30, 40], [190, 22], [150, 40 + 90 * mouth], [30, 60 + 40 * mouth]], { fill: '#3A1420', lw: 5, seed: seed + 14, step: 18 });
    for (let k = 0; k < 4; k++) G.poly(ctx, [[60 + k * 30, 40], [80 + k * 30, 40], [70 + k * 30, 66]], { fill: '#FFFDF4', lw: 2.5, seed: seed + 20 + k, step: 6 });
    // crown
    G.poly(ctx, [[-60, -96], [40, -100], [52, -170], [20, -130], [-6, -185], [-30, -130], [-70, -165]], { fill: '#F2B84B', lw: 5, seed: seed + 30, step: 14 });
    G.ellipse(ctx, -6, -122, 9, 9, { fill: '#D8282E', lw: 2, seed: seed + 31 });
    ctx.restore();
    ctx.restore();
  }
  // a small red drake
  function drake(ctx, o) {
    const { x, y = FEET, s = 1, t = G.t, seed = 2200, face = 1, scared = 0 } = o;
    ctx.save(); ctx.translate(x, y); ctx.scale(s * face, s);
    ctx.fillStyle = 'rgba(20,10,20,0.2)'; ctx.beginPath(); ctx.ellipse(0, 4, 90, 12, 0, 0, Math.PI * 2); ctx.fill();
    const flap = Math.sin(t * 7) * 0.25;
    G.line(ctx, [[-50, -60], [-110, -40], [-140, -80]], { color: '#C9442E', lw: 18, seed: seed + 1, step: 14 });
    ctx.save(); ctx.translate(-10, -110); ctx.rotate(-0.5 + flap);
    G.poly(ctx, [[0, 0], [-40, -110], [-10, -80], [20, -120], [30, -40]], { fill: '#F08A4B', lw: 4, seed: seed + 2, step: 16 }); ctx.restore();
    for (const lx of [-35, 35]) G.limb(ctx, [[lx, -40], [lx, -4]], { color: '#C9442E', lw: 18, seed: seed + 3 + lx });
    G.ellipse(ctx, 0, -70, 70, 48, { fill: '#D9533A', lw: 4.5, seed: seed + 5, hatch: { color: 'rgba(80,10,10,0.18)', gap: 8 } });
    G.ellipse(ctx, 0, -58, 40, 26, { fill: '#F6C27A', lw: 0, seed: seed + 6, amp: 0.5 });
    G.ellipse(ctx, 70, -130, 44, 36, { fill: '#D9533A', lw: 4.5, seed: seed + 7 });
    for (const hx of [52, 80]) G.poly(ctx, [[hx, -160], [hx + 8, -195], [hx + 16, -158]], { fill: '#F6E2B0', lw: 3, seed: seed + 8 + hx, step: 8 });
    G.ellipse(ctx, 82, -138, scared ? 11 : 8, scared ? 12 : 9, { fill: scared ? '#FFF' : INK, lw: scared ? 3 : 0, seed: seed + 9 });
    if (scared) { ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(82, -138, 4, 0, Math.PI * 2); ctx.fill(); }
    G.line(ctx, [[94, -114], [112, -118]], { lw: 3.5, seed: seed + 10 });
    ctx.restore();
  }
  function wolf(ctx, o) { Ch.dog(ctx, { pose: 'stand', color: '#9A9AA8', ear: '#6E6E7C', happy: 0.3, seed: 2300, ...o }); }
  function hawk(ctx, o) { Ch.bird(ctx, { color: '#A87A4E', s: 1.6, seed: 2400, ...o }); }
  function cloak(ctx, x, y, s, t, face = 1) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    const w = Math.sin(t * 2) * 10;
    G.poly(ctx, [[-70, -310], [70, -310], [120 + w, -10], [40, 6], [-40, 6], [-120 + w, -10]], { fill: '#A51E2A', lw: 5, seed: 2500, step: 24, hatch: { color: 'rgba(60,0,0,0.25)', gap: 10 } });
    ctx.restore();
  }

  // a person with a mood
  function P(ctx, who, x, o = {}) {
    const t = G.t; const mood = MOOD[o.mood || 'neutral'];
    let px = x, extra = {};
    if (o.walk) { const w = Ch.walk(t, { x0: x, speed: o.walk, t0: o.t0 || 0, stride: 260 * (o.s || 1) }); px = w.x; extra = { pose: 'walk', walk: w.walk }; }
    if (who === 'cassian') cloak(ctx, px, (o.y || FEET), o.s || 1, t);
    Ch.person(ctx, { x: px, y: (o.y || FEET) - (o.hop || 0), s: o.s || 1, sx: o.face || 1, pose: 'stand', style: CAST[who], ...mood, mouth: o.mouth || mood.mouth, gesture: o.gesture || null, look: o.look ?? 0, lookY: o.lookY ?? 0, sweat: o.sweat || (o.mood === 'scared' ? 0.8 : 0), blush: o.blush || 0, seed: o.seed || (3000 + who.length * 97), ...extra });
    if (o.mood === 'laugh') for (const sd of [-1, 1]) G.text(ctx, 'HA', px + sd * 120 * (o.s || 1), (o.y || FEET) - 470 * (o.s || 1) - Math.abs(Math.sin(t * 9)) * 14, { size: 44, fam: 'Bungee', weight: 400, align: 'center', color: '#F6F0E2', stroke: INK, strokeW: 7 });
    if (who === 'pip' && o.ribbon) G.poly(ctx, [[px - 30, (o.y || FEET) - 380 * (o.s || 1)], [px, (o.y || FEET) - 360 * (o.s || 1)], [px - 30, (o.y || FEET) - 340 * (o.s || 1)]], { fill: '#D8282E', lw: 3, seed: 3333, step: 8 });
    return px;
  }

  // ---------------- backgrounds ----------------
  function sky(ctx, top = '#8FC6E6', bot = '#E9F3F2') {
    const g = ctx.createLinearGradient(0, 0, 0, 1200); g.addColorStop(0, top); g.addColorStop(1, bot);
    ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, H + 600);
  }
  function clouds(ctx, t) {
    for (let i = 0; i < 4; i++) {
      const x = ((i * 380 + t * (14 + i * 4)) % (W + 500)) - 250, y = 260 + i * 120;
      ctx.save(); ctx.globalAlpha = 0.9;
      for (const [dx, dy, r] of [[0, 0, 60], [60, -20, 70], [130, 0, 56], [70, 20, 60]]) G.ellipse(ctx, x + dx, y + dy, r, r * 0.7, { fill: '#FFFFFF', lw: 0, seed: 4000 + i * 7 + dx, amp: 0.5 });
      ctx.restore();
    }
  }
  const WALLS = ['#EAD9B8', '#E7C9A1', '#DDE3D4', '#E9D3C5', '#D9CDB4'];
  const ROOFS = ['#B5543C', '#8E4A3A', '#A8613F', '#7E5B4A'];
  function houseRow(ctx, base, { night = false, seed = 10, scale = 1, lit = 0 } = {}) {
    let x = -60, k = 0;
    while (x < W + 60) {
      const w = (170 + (G.rnd(seed, k) * 80)) * scale, h = (330 + G.rnd(seed, k, 2) * 220) * scale;
      const wall = night ? '#2E3358' : WALLS[(k + seed) % WALLS.length], roof = night ? '#1E2240' : ROOFS[(k + seed) % ROOFS.length];
      G.rrect(ctx, x, base - h, w, h, 4, { fill: wall, lw: 4, seed: seed * 100 + k, hatch: night ? null : { color: 'rgba(90,60,30,0.10)', gap: 12 } });
      if (!night) for (const bx of [x + 8, x + w - 20]) G.line(ctx, [[bx, base - h + 6], [bx, base - 4]], { color: '#7A5A3A', lw: 6, seed: seed * 100 + k + bx });
      G.poly(ctx, [[x - 18, base - h], [x + w + 18, base - h], [x + w / 2, base - h - 110 * scale]], { fill: roof, lw: 4, seed: seed * 100 + k + 50, step: 20 });
      for (let r = 0; r < 2; r++) for (let c = 0; c < 2; c++) {
        const wx = x + 30 * scale + c * (w - 100 * scale), wy = base - h + 50 * scale + r * 130 * scale;
        if (wy + 80 * scale > base - 90 * scale) continue;
        const on = night && G.rnd(seed, k, r, c) < 0.6 + lit;
        G.rrect(ctx, wx, wy, 44 * scale, 74 * scale, 5, { fill: night ? (on ? '#F2C25B' : '#1A1D33') : '#6F93A6', lw: 3.5, seed: seed * 100 + k + r * 3 + c });
        if (!night) G.line(ctx, [[wx + 22 * scale, wy + 2], [wx + 22 * scale, wy + 72 * scale]], { lw: 2.5, seed: seed + k + r + c });
      }
      G.rrect(ctx, x + w / 2 - 26 * scale, base - 100 * scale, 52 * scale, 100 * scale, 20, { fill: night ? '#151729' : '#7A4E2E', lw: 4, seed: seed * 100 + k + 70 });
      x += w + 6; k++;
    }
  }
  function ground(ctx, col = '#CDBB98', y = 1150, night = false) {
    G.rrect(ctx, -40, y, W + 80, H - y + 60, 0, { fill: night ? '#262A45' : col, lw: 4, seed: 4100, hatch: { color: night ? 'rgba(255,255,255,0.04)' : 'rgba(90,60,30,0.12)', gap: 14, angle: 0.2 } });
    if (!night) for (let i = 0; i < 14; i++) G.ellipse(ctx, 40 + i * 80 + (i % 2) * 30, y + 60 + (i % 3) * 120, 26, 10, { fill: 'rgba(120,95,60,0.25)', lw: 0, seed: 4120 + i });
  }
  function street(ctx, t) { sky(ctx); clouds(ctx, t); houseRow(ctx, 1160, { seed: 3, scale: 0.75 }); ground(ctx); }
  function stone(ctx, x, y, s = 1, cracked = 0, glow = 0) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    G.rrect(ctx, -150, -40, 300, 50, 8, { fill: '#9C9486', lw: 5, seed: 4200 });
    G.poly(ctx, [[-110, -40], [110, -40], [96, -520], [40, -600], [-50, -590], [-100, -500]], { fill: '#8C93A4', lw: 6, seed: 4201, step: 26, hatch: { color: 'rgba(30,30,60,0.2)', gap: 10, angle: 0.8 } });
    const rc = glow > 0 ? `rgba(${120 + 135 * glow},${200 - 120 * glow},255,1)` : '#7FD4F0';
    for (let k = 0; k < 4; k++) G.line(ctx, [[-40 + k * 26, -440 + (k % 2) * 30], [-30 + k * 26, -360]], { color: rc, lw: 8, seed: 4210 + k });
    if (cracked > 0) {
      G.line(ctx, [[0, -600], [-20, -470], [24, -360], [-14, -220], [20, -40]].map(([a, b]) => [a, lerp(-600, b, clamp(cracked))]), { color: INK, lw: 9, seed: 4220 });
      if (cracked > 0.5) G.line(ctx, [[-20, -470], [-80, -420]], { color: INK, lw: 7, seed: 4221 });
    }
    ctx.restore();
  }
  function bunting(ctx, y = 420) {
    const cols = ['#D8533A', '#F2B84B', '#3D7A74', '#E8718D'];
    G.line(ctx, [[-20, y], [W / 2, y + 60], [W + 20, y]], { lw: 3, seed: 4300, step: 40 });
    for (let k = 0; k < 11; k++) { const x = k * 105 + 20, yy = y + 60 * (1 - Math.pow((x - W / 2) / (W / 2), 2)); G.poly(ctx, [[x, yy], [x + 70, yy + 4], [x + 33, yy + 70]], { fill: cols[k % 4], lw: 3, seed: 4310 + k, step: 12 }); }
  }
  function square(ctx, t, o = {}) { street(ctx, t); bunting(ctx); stone(ctx, o.sx ?? 540, 1190, o.ss ?? 0.9, o.crack || 0, o.glow || 0); }
  function home(ctx, t) {
    ctx.fillStyle = '#9B7656'; ctx.fillRect(-300, -300, W + 600, H + 600);
    for (let x = -40; x < W + 40; x += 120) G.rrect(ctx, x, 200, 118, 960, 2, { fill: x % 240 ? '#A5805E' : '#987252', lw: 3, seed: 4400 + x, hatch: { color: 'rgba(60,35,20,0.12)', gap: 16, angle: 1.5 } });
    G.rrect(ctx, 120, 420, 260, 240, 8, { fill: '#BFE0F0', lw: 6, seed: 4450 });
    G.line(ctx, [[250, 422], [250, 658]], { lw: 6, seed: 4451 }); G.line(ctx, [[122, 540], [378, 540]], { lw: 6, seed: 4452 });
    G.rrect(ctx, 600, 520, 300, 30, 6, { fill: '#7A5A3E', lw: 4, seed: 4460 });
    for (const [px, c] of [[640, '#C9C2B4'], [720, '#B5543C'], [800, '#D9CDB4']]) G.rrect(ctx, px, 470, 50, 50, 10, { fill: c, lw: 3.5, seed: 4461 + px });
    ctx.save(); const g = ctx.createRadialGradient(250, 540, 50, 250, 540, 900); g.addColorStop(0, 'rgba(255,230,170,0.35)'); g.addColorStop(1, 'rgba(255,230,170,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
    ground(ctx, '#8A6648', 1150);
  }
  function table(ctx, x = 760, broken = false) {
    G.rrect(ctx, x - 200, 1000, broken ? 220 : 400, 34, 6, { fill: '#8E6444', lw: 5, seed: 4500 });
    for (const lx of broken ? [x - 180] : [x - 180, x + 170]) G.rrect(ctx, lx, 1030, 22, 220, 4, { fill: '#7A5236', lw: 4, seed: 4501 + lx });
    if (broken) G.poly(ctx, [[x + 20, 1000], [x + 30, 1034], [x + 5, 1030]], { fill: '#8E6444', lw: 3, seed: 4505, step: 8 });
  }
  function yard(ctx, t) {
    sky(ctx, '#F4C58F', '#F8E6C8'); clouds(ctx, t);
    for (let x = -20; x < W + 40; x += 70) G.rrect(ctx, x, 820, 56, 340, 6, { fill: '#B98A5E', lw: 4, seed: 4600 + x });
    G.rrect(ctx, -20, 880, W + 40, 26, 4, { fill: '#A07548', lw: 4, seed: 4650 }); G.rrect(ctx, -20, 1030, W + 40, 26, 4, { fill: '#A07548', lw: 4, seed: 4651 });
    ground(ctx, '#C7B07E');
  }
  function dummy(ctx, x, y = FEET, wob = 0, alpha = 1) {
    ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, y); ctx.rotate(wob);
    G.rrect(ctx, -10, -330, 20, 330, 4, { fill: '#7A5236', lw: 4, seed: 4700 });
    G.rrect(ctx, -110, -300, 220, 24, 6, { fill: '#7A5236', lw: 4, seed: 4701 });
    G.ellipse(ctx, 0, -230, 70, 90, { fill: '#E2C46A', lw: 5, seed: 4702, hatch: { color: 'rgba(120,80,20,0.35)', gap: 7, angle: 1.4 } });
    G.ellipse(ctx, 0, -370, 56, 56, { fill: '#E2C46A', lw: 5, seed: 4703, hatch: { color: 'rgba(120,80,20,0.35)', gap: 7, angle: 1.4 } });
    for (const sd of [-1, 1]) G.line(ctx, [[sd * 20 - 10, -385], [sd * 20 + 10, -365]], { lw: 5, seed: 4704 + sd });
    ctx.restore();
  }
  function night(ctx, t, o = {}) {
    const g = ctx.createLinearGradient(0, 0, 0, 1200); g.addColorStop(0, '#0F1430'); g.addColorStop(1, '#2C2B5A');
    ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, H + 600);
    for (let i = 0; i < 70; i++) { const x = G.rnd(i, 1) * W, y = G.rnd(i, 2) * 900, tw = 0.5 + 0.5 * Math.sin(t * 2 + i); ctx.fillStyle = `rgba(240,240,255,${0.3 + 0.6 * tw})`; ctx.beginPath(); ctx.arc(x, y, 1.5 + G.rnd(i, 3) * 2, 0, Math.PI * 2); ctx.fill(); }
    const mg = ctx.createRadialGradient(800, 380, 40, 800, 380, 320); mg.addColorStop(0, 'rgba(255,250,220,0.35)'); mg.addColorStop(1, 'rgba(255,250,220,0)'); ctx.fillStyle = mg; ctx.fillRect(400, 0, 800, 800);
    G.ellipse(ctx, 800, 380, 80, 80, { fill: '#F3EFD6', lw: 3, seed: 4800 });
    houseRow(ctx, 1160, { night: true, seed: 5, scale: 0.75 });
    ground(ctx, null, 1150, true);
    if (o.roofman) { // a silhouette on the rooftops
      ctx.save(); ctx.translate(o.roofman[0], o.roofman[1]); ctx.scale(0.42, 0.42); cloak(ctx, 0, 0, 1, t);
      Ch.person(ctx, { x: 0, y: 0, s: 1, pose: 'stand', style: CAST.cassian, eyes: 'normal', brows: 'determined', mouth: 'smirk', seed: 5000 }); ctx.restore();
    }
  }
  function sewer(ctx, t, o = {}) {
    ctx.fillStyle = '#1F2B2A'; ctx.fillRect(-300, -300, W + 600, H + 600);
    for (let r = 0; r < 14; r++) for (let c = 0; c < 8; c++) {
      const x = c * 150 - (r % 2) * 75 - 20, y = 140 + r * 74;
      if (y > 1120) continue;
      G.rrect(ctx, x, y, 144, 68, 6, { fill: (r + c) % 3 ? '#2E3E3B' : '#33453F', lw: 3, seed: 5100 + r * 10 + c, amp: 0.6 });
    }
    G.shape(ctx, G.ellPts(540, 700, 220, 280), { fill: '#141C1B', lw: 8, seed: 5200 });
    G.rrect(ctx, -40, 1150, W + 80, H, 0, { fill: '#26332F', lw: 4, seed: 5201 });
    G.rrect(ctx, -40, 1290, W + 80, 80, 0, { fill: '#3E6B4E', lw: 4, seed: 5202, hatch: { color: 'rgba(160,220,160,0.18)', gap: 12, angle: 0 } });
    for (let i = 0; i < 3; i++) { const dy = ((t * 300 + i * 260) % 900); G.ellipse(ctx, 200 + i * 330, 160 + dy, 5, 9, { fill: '#7FB8A0', lw: 0, seed: 5210 + i }); }
    const torch = o.torch ?? 1;
    if (torch > 0) {
      const fl = 1 + Math.sin(t * 17) * 0.04 + Math.sin(t * 7) * 0.05;
      G.rrect(ctx, 120, 560, 20, 100, 4, { fill: '#5A3A22', lw: 4, seed: 5220 });
      G.poly(ctx, [[110, 560], [150, 560], [140 + Math.sin(t * 13) * 6, 500 - 30 * fl * torch], [130, 520]], { fill: '#F2B84B', lw: 3, seed: 5221, step: 10 });
    }
  }
  // the torch light / darkness over a sewer shot
  function sewerLight(ctx, torch = 1, cx = 300, cy = 800) {
    ctx.save();
    const r = 300 + 900 * torch;
    const g = ctx.createRadialGradient(cx, cy, 60, cx, cy, r);
    g.addColorStop(0, 'rgba(255,190,110,0.0)'); g.addColorStop(0.55, `rgba(10,8,20,${0.12 + 0.35 * (1 - torch)})`); g.addColorStop(1, `rgba(5,4,12,${0.45 + 0.35 * (1 - torch)})`);
    ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, H + 600);
    ctx.globalCompositeOperation = 'screen';
    const w = ctx.createRadialGradient(cx, cy, 10, cx, cy, 500);
    w.addColorStop(0, `rgba(255,170,80,${0.25 * torch})`); w.addColorStop(1, 'rgba(255,170,80,0)');
    ctx.fillStyle = w; ctx.fillRect(-300, -300, W + 600, H + 600);
    ctx.restore();
  }
  function voidBg(ctx, t, col = '#6C3FC9') {
    ctx.fillStyle = '#0D0A16'; ctx.fillRect(-300, -300, W + 600, H + 600);
    const g = ctx.createRadialGradient(540, 900, 50, 540, 900, 900); g.addColorStop(0, col + '88'); g.addColorStop(1, '#0D0A1600');
    ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, H + 600);
    for (let i = 0; i < 30; i++) { const y = (1500 - ((t * 80 + i * 97) % 1500)), x = G.rnd(i, 9) * W; ctx.fillStyle = 'rgba(200,170,255,0.5)'; ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2); ctx.fill(); }
  }
  function bars(ctx) {
    for (let x = 40; x < W; x += 110) G.rrect(ctx, x, -40, 26, 1350, 6, { fill: '#3B3E46', lw: 5, seed: 5300 + x });
    G.rrect(ctx, -20, 380, W + 40, 34, 6, { fill: '#3B3E46', lw: 5, seed: 5390 });
    G.rrect(ctx, -20, 980, W + 40, 34, 6, { fill: '#3B3E46', lw: 5, seed: 5391 });
  }
  function dim(ctx, a, col = '8,6,18') { if (a <= 0) return; ctx.fillStyle = `rgba(${col},${a})`; ctx.fillRect(-300, -300, W + 600, H + 600); }

  // ---------------- UI overlays (screen space) ----------------
  const UIY = SAFE.y + 40;
  function stamp(ctx, text, t, t0, { color = '#F2B84B', y = UIY + 160, size = 130, rot = -0.06 } = {}) {
    if (t < t0) return;
    const k = ease.outBack(clamp((t - t0) / 0.18), 2.6);
    ctx.save(); ctx.translate(W / 2 - 50, y); ctx.rotate(rot); ctx.scale(k, k);
    G.text(ctx, text, 0, 0, { size, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color, stroke: INK, strokeW: 16 });
    ctx.restore();
  }
  function label(ctx, text, t, t0, color = '#F2B84B') {
    if (t < t0) return;
    const k = ease.outBack(clamp((t - t0) / 0.25), 1.8);
    ctx.save(); ctx.translate(W / 2 - 50, UIY + 20); ctx.scale(k, k);
    G.tornPaper(ctx, -260, -48, 520, 96, { fill: '#2A2320', seed: 5400, shadow: true });
    G.text(ctx, text, 0, 4, { size: 46, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color });
    ctx.restore();
  }
  function board(ctx, t, t0, { title = 'PET POWER', from = 0, to = 100, d = 1.2, color = '#6FE08A', sub = null, glitch = false } = {}) {
    const k = ease.outBack(clamp((t - t0) / 0.3), 1.6);
    if (k <= 0) return;
    ctx.save(); ctx.translate(W / 2 - 50, UIY + 160); ctx.scale(k, k);
    G.rrect(ctx, -230, -150, 460, 300, 26, { fill: '#1E1B26', lw: 7, seed: 5500 });
    G.rrect(ctx, -205, -125, 410, 250, 18, { fill: '#2A2635', lw: 3, seed: 5501, amp: 0.4 });
    G.text(ctx, title, 0, -82, { size: 34, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color: '#C9C2D6' });
    let txt, col = color;
    const u = clamp((t - t0 - 0.3) / d);
    if (glitch && u >= 1) { txt = '???'; col = '#FF5A5A'; }
    else if (glitch && u > 0) { txt = String(Math.floor(G.rnd(Math.floor(t * 20)) * 9999)); col = ['#FF5A5A', '#F2B84B', '#6FE08A'][Math.floor(t * 20) % 3]; }
    else txt = Math.round(lerp(from, to, ease.outCubic(u))).toLocaleString('en-US');
    const pop = u >= 1 ? 1 + 0.12 * Math.exp(-(t - t0 - 0.3 - d) * 8) : 1;
    ctx.save(); ctx.translate(0, 20); ctx.scale(pop, pop);
    G.text(ctx, txt, 0, 0, { size: 130, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color: col, stroke: INK, strokeW: 10 });
    ctx.restore();
    if (sub) { G.rrect(ctx, -170, 92, 340, 44, 12, { fill: col, lw: 4, seed: 5502 }); G.text(ctx, sub, 0, 116, { size: 26, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color: INK }); }
    ctx.restore();
  }
  function panel(ctx, t, t0, title, lines, { color = '#B98CFF', y = UIY + 60 } = {}) {
    const k = clamp((t - t0) / 0.25); if (k <= 0) return;
    const h = 120 + lines.length * 62;
    ctx.save(); ctx.translate(W / 2 - 50, y); ctx.globalAlpha = k; ctx.scale(lerp(0.85, 1, ease.outBack(k)), lerp(0.85, 1, ease.outBack(k)));
    ctx.shadowColor = color; ctx.shadowBlur = 40;
    G.rrect(ctx, -390, 0, 780, h, 20, { fill: 'rgba(16,12,30,0.92)', lw: 6, stroke: color, seed: 5600 });
    ctx.shadowBlur = 0;
    G.text(ctx, title, 0, 56, { size: 40, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color });
    G.line(ctx, [[-340, 94], [340, 94]], { color, lw: 3, seed: 5601 });
    let chars = Math.floor((t - t0 - 0.3) * 38);
    lines.forEach((ln, i) => {
      const shown = ln.slice(0, Math.max(0, chars)); chars -= ln.length;
      G.text(ctx, shown, -350, 140 + i * 62, { size: 40, baseline: 'middle', fam: 'Patrick Hand', weight: 400, color: '#F2EEFF' });
    });
    ctx.restore();
  }
  function card(ctx, t, t0, name, rarity, stat, color = '#B98CFF') {
    const k = ease.outBack(clamp((t - t0) / 0.35), 1.8); if (k <= 0) return;
    ctx.save(); ctx.translate(W / 2 - 50, UIY + 200); ctx.scale(k, k); ctx.rotate(-0.03);
    ctx.shadowColor = color; ctx.shadowBlur = 50;
    G.rrect(ctx, -290, -170, 580, 340, 26, { fill: '#18132A', lw: 7, stroke: color, seed: 5700 });
    ctx.shadowBlur = 0;
    G.text(ctx, 'NEW', 0, -118, { size: 30, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color: '#F2B84B' });
    G.text(ctx, name, 0, -40, { size: 66, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color: '#FFFFFF' });
    G.rrect(ctx, -140, 18, 280, 50, 14, { fill: color, lw: 4, seed: 5701 });
    G.text(ctx, rarity, 0, 44, { size: 30, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color: INK });
    G.text(ctx, stat, 0, 116, { size: 42, align: 'center', baseline: 'middle', fam: 'Patrick Hand', weight: 400, color: '#9EF0B0' });
    ctx.restore();
  }
  function hp(ctx, t, name, frac) {
    ctx.save(); ctx.translate(W / 2 - 50, UIY + 10);
    G.rrect(ctx, -330, -26, 660, 52, 14, { fill: '#1E1B26', lw: 6, seed: 5800 });
    G.rrect(ctx, -320, -16, 640 * clamp(frac), 32, 8, { fill: '#E0403E', lw: 0, seed: 5801, amp: 0.3 });
    G.text(ctx, name, 0, 62, { size: 34, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color: '#FFFFFF', stroke: INK, strokeW: 8 });
    ctx.restore();
  }
  function counter(ctx, t, t0, lab, from, to, d = 1.2, color = '#F2B84B') {
    const v = Math.round(lerp(from, to, ease.outCubic(clamp((t - t0) / d))));
    ctx.save(); ctx.translate(W - 170 - 150, UIY + 10);
    G.rrect(ctx, -150, -42, 300, 84, 20, { fill: '#1E1B26', lw: 5, seed: 5900 });
    G.ellipse(ctx, -100, 0, 24, 24, { fill: color, lw: 4, seed: 5901 });
    G.text(ctx, lab, -60, 0, { size: 28, baseline: 'middle', fam: 'Bungee', weight: 400, color: '#C9C2D6' });
    G.text(ctx, String(v), 130, 2, { size: 46, align: 'right', baseline: 'middle', fam: 'Bungee', weight: 400, color });
    ctx.restore();
  }
  function tag(ctx, text, x, y, color = '#F6F0E2') {
    ctx.save(); const w = text.length * 20 + 50;
    G.rrect(ctx, x - w / 2, y - 30, w, 60, 16, { fill: '#1E1B26', lw: 4, stroke: color, seed: 6000 + text.length });
    G.text(ctx, text, x, y + 2, { size: 28, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color });
    ctx.restore();
  }
  function floaty(ctx, t, t0, text, x, y, color = '#FF6A5A') {
    const a = t - t0; if (a < 0 || a > 1.1) return;
    ctx.save(); ctx.globalAlpha = 1 - clamp((a - 0.6) / 0.5);
    G.text(ctx, text, x, y - a * 120, { size: 54, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color, stroke: INK, strokeW: 9 });
    ctx.restore();
  }
  function beam(ctx, x, t, t0, color = '#B98CFF') {
    const k = clamp((t - t0) / 0.3); if (k <= 0) return;
    ctx.save(); ctx.globalCompositeOperation = 'screen';
    const g = ctx.createLinearGradient(x - 90, 0, x + 90, 0); g.addColorStop(0, color + '00'); g.addColorStop(0.5, color + 'CC'); g.addColorStop(1, color + '00');
    ctx.fillStyle = g; ctx.globalAlpha = k * (0.85 + 0.15 * Math.sin(t * 9)); ctx.fillRect(x - 90, -200, 180, FEET + 200);
    ctx.restore();
  }

  // ---------------- the shots (one per voiceover line) ----------------
  const L = (i) => S.SHOTS[i].t;
  const SH = [];
  const add = (i, draw, o = {}) => SH.push({ at: L(i), draw, in: o.in || 'cut', cam: o.cam || Shots.push(1.0, 1.05) });
  const C = (k) => (s) => ({ zoom: lerp(k[0], k[1], ease.inOutQuad(s.u)), x: k[2] || 0, y: k[3] || 0 });

  // ACT 1
  add(0, (ctx, t, s) => { square(ctx, t); P(ctx, 'tess', 170, { s: 0.85 }); wolf(ctx, { x: 330, y: FEET, s: 0.7 }); P(ctx, 'brann', 800, { s: 0.95, face: -1 }); P(ctx, 'kid', 960, { s: 0.8, face: -1, mood: 'happy' }); label(ctx, '7 DAYS LEFT', t, s.t0 + 0.6, '#FF6A5A'); }, { cam: C([1.25, 1.0, 0, -150]) });
  add(1, (ctx, t, s) => { square(ctx, t, { glow: clamp(s.dt / 2) }); board(ctx, t, s.t0 + 0.1, { from: 0, to: 100, sub: 'OVER 100 = CONTRACT' }); }, { cam: C([1.05, 1.12, 0, 150]) });
  add(2, (ctx, t, s) => { square(ctx, t); P(ctx, 'guild', 360, { s: 1.15, mood: 'smirk', gesture: 'point' }); hawk(ctx, { x: 760, y: 820 + Math.sin(t * 3) * 12, facing: -1, t }); dim(ctx, 0.25); label(ctx, 'UNDER 100 = TAKEN', t, s.t0 + 0.8, '#FF6A5A'); });
  add(3, (ctx, t, s) => { home(ctx, t); table(ctx); P(ctx, 'mom', 260, { s: 1.05, mood: 'sad' }); P(ctx, 'pip', 450, { s: 0.7, mood: 'sad', look: 1 }); P(ctx, 'milo', 760, { s: 1.0, face: -1, mood: 'neutral' }); }, { in: 'fade' });
  add(4, (ctx, t, s) => { home(ctx, t); table(ctx); for (let k = 0; k < 3; k++) G.ellipse(ctx, 700 + k * 60, 985 - (k === 1 ? 6 : 0), 26, 12, { fill: '#F2B84B', lw: 4, seed: 6100 + k }); P(ctx, 'pip', 450, { s: 0.7, mood: 'sad', look: 1 }); counter(ctx, t, s.t0, 'COINS', 3, 3); }, { cam: C([1.35, 1.5, 180, 0]) });
  add(5, (ctx, t, s) => { square(ctx, t); P(ctx, 'milo', 230, { s: 1.05, mood: 'sad' }); bob(ctx, { x: 560, r: 60, mood: 'sad', t }); board(ctx, t, s.t0 + 0.1, { from: 0, to: 2, d: 0.4, color: '#FF6A5A', sub: 'SLIME · COMMON' }); });
  add(6, (ctx, t, s) => { street(ctx, t); P(ctx, 'milo', 330, { s: 1.15, mood: 'happy', gesture: 'wave' }); const top = bob(ctx, { x: 640, r: 72, t, squash: 0.08 * Math.max(0, Math.sin((t - s.t0) * 6)) }); tag(ctx, 'BOB · LV 1', 640, top - 50, '#9EF0B0'); }, { in: 'whip', cam: C([1.3, 1.38, 0, 120]) });
  add(7, (ctx, t, s) => { street(ctx, t); const top = bob(ctx, { x: 490, r: 90, mood: 'sad', t }); tag(ctx, 'ATK 1 · DEF 1', 490, top - 50, '#FF8A7A'); label(ctx, 'RANK: DEAD LAST', t, s.t0 + 0.5, '#FF6A5A'); }, { cam: C([1.5, 1.6, 0, 200]) });
  add(8, (ctx, t, s) => { street(ctx, t); P(ctx, 'tess', 330, { s: 1.15, mood: 'happy' }); wolf(ctx, { x: 660, y: FEET, s: 1.0, happy: 0.9, t }); beam(ctx, 660, t, s.t0 + 1.4, '#6FE08A'); tag(ctx, 'ASH · LV 9', 660, FEET - 300, '#9EF0B0'); }, { cam: C([1.2, 1.26, 0, 120]) });
  add(9, (ctx, t, s) => { street(ctx, t); beam(ctx, 680, t, s.t0 + 1.0, '#F2B84B'); P(ctx, 'rolf', 330, { s: 1.15, mood: 'laugh', gesture: 'cheer' }); drake(ctx, { x: 680, s: 1.25, t, face: -1 }); tag(ctx, 'DRAKE · LV 15', 680, FEET - 330, '#F2B84B'); }, { cam: C([1.2, 1.26, 0, 120]) });
  add(10, (ctx, t, s) => { street(ctx, t); P(ctx, 'milo', 330, { s: 1.15, mood: 'neutral', look: 1 }); bob(ctx, { x: 640, r: 60, t, mood: 'happy' }); }, { cam: C([1.25, 1.45, 60, 160]) });
  add(11, (ctx, t, s) => { street(ctx, t); G.rrect(ctx, 40, 1000, 420, 22, 4, { fill: '#B98A5E', lw: 4, seed: 6200 }); const fall = ease.inQuad(clamp((s.dt - 1.4) / 0.4)); ctx.save(); ctx.translate(200, lerp(-160, 0, fall)); ctx.rotate(fall * 1.3); P(ctx, 'rolf', 0, { s: 0.95, mood: 'laugh', y: FEET }); ctx.restore(); drake(ctx, { x: 420, s: 0.85, t }); bob(ctx, { x: 640, r: 50, mood: 'sad', t }); P(ctx, 'milo', 850, { s: 1.0, face: -1, mood: 'sad' }); if (fall >= 1) stamp(ctx, 'THUD', t, s.t0 + 1.8, { color: '#F6F0E2', y: 900, size: 90 }); });
  // ACT 2: the habit
  add(12, (ctx, t, s) => { home(ctx, t); bob(ctx, { x: 540, r: 90, t, mood: 'wide' }); stamp(ctx, '?', t, s.t0 + 0.4, { color: '#F6F0E2', y: 650, size: 160, rot: 0.1 }); }, { in: 'fade', cam: C([1.3, 1.45, 0, 200]) });
  add(13, (ctx, t, s) => { home(ctx, t); bob(ctx, { x: 540, r: 100, t, mood: 'chomp', squash: 0.12 * Math.sin(s.dt * 16) }); stamp(ctx, 'CHOMP!', t, s.t0 + 0.5); }, { in: 'flash', cam: Shots.combine(C([1.35, 1.4, 0, 200]), Shots.shake(14, L(13) + 0.5, 6)) });
  add(14, (ctx, t, s) => { home(ctx, t); table(ctx, 760, s.dt > 1.9); P(ctx, 'mom', 900, { s: 1.0, face: -1, mood: s.dt > 1.9 ? 'shock' : 'angry' }); bob(ctx, { x: 420, r: lerp(70, 90, clamp(s.dt / 2.5)), t, mood: 'chomp', squash: 0.1 * Math.sin(s.dt * 14) }); floaty(ctx, t, s.t0 + 0.2, '-1 BOOT', 420, 800); floaty(ctx, t, s.t0 + 0.9, '-1 SPOON', 440, 780); floaty(ctx, t, s.t0 + 1.8, '-½ TABLE', 520, 760); });
  add(15, (ctx, t, s) => { home(ctx, t); G.rrect(ctx, 820, 640, 200, 520, 10, { fill: '#6B4428', lw: 6, seed: 6300 }); P(ctx, 'mom', 380, { s: 1.15, mood: 'angry', gesture: 'point' }); bob(ctx, { x: 720, r: 60, mood: 'sad', t }); }, { cam: C([1.2, 1.28, 0, 120]) });
  add(16, (ctx, t, s) => { yard(ctx, t); dummy(ctx, 820); P(ctx, 'milo', 260, { s: 1.1, mood: 'brave', gesture: 'cheer' }); bob(ctx, { x: 520, r: 60, t, mood: 'happy' }); label(ctx, 'TRAINING: DAY 1', t, s.t0 + 0.3, '#F2B84B'); }, { in: 'fade' });
  add(17, (ctx, t, s) => { yard(ctx, t); dummy(ctx, 760, FEET, Math.sin(s.dt * 10) * 0.03); const j = Math.sin(clamp(s.dt / 0.8) * Math.PI); bob(ctx, { x: lerp(420, 600, clamp(s.dt / 0.8)), y: FEET - j * 200, r: 60, t, mood: 'chomp' }); }, { cam: C([1.3, 1.35, 60, 150]) });
  add(18, (ctx, t, s) => { yard(ctx, t); dummy(ctx, 760); const b = Math.abs(Math.sin(s.dt * 5)) * 150 * Math.exp(-s.dt * 1.2); bob(ctx, { x: 500 - s.dt * 60, y: FEET - b, r: 60, t, mood: 'sad', squash: b < 10 ? 0.15 : -0.1 }); floaty(ctx, t, s.t0 + 0.1, 'MISS', 640, 800, '#F6F0E2'); floaty(ctx, t, s.t0 + 1.0, 'MISS', 560, 780, '#F6F0E2'); }, { cam: C([1.3, 1.35, 60, 150]) });
  add(19, (ctx, t, s) => { yard(ctx, t); const gone = s.dt > 0.7; if (!gone) dummy(ctx, 700, FEET, 0, 1); bob(ctx, { x: 650, r: gone ? 100 : 70, t, mood: gone ? 'happy' : 'chomp', squash: gone ? 0 : 0.2 }); if (gone) stamp(ctx, 'GULP.', t, s.t0 + 0.7, { color: '#F6F0E2' }); }, { cam: Shots.combine(C([1.3, 1.3, 60, 150]), Shots.shake(12, L(19) + 0.7, 6)) });
  add(20, (ctx, t, s) => { yard(ctx, t); P(ctx, 'milo', 260, { s: 1.1, mood: 'sad' }); bob(ctx, { x: 620, r: 100, t, mood: 'happy' }); board(ctx, t, s.t0, { from: 2, to: 2, d: 0.2, color: '#FF6A5A', sub: 'STILL COMMON' }); });
  // the hint
  add(21, (ctx, t, s) => { night(ctx, t); P(ctx, 'milo', 300, { s: 1.1, mood: 'neutral', look: 1 }); bob(ctx, { x: 640, r: 64, t, mood: 'happy' }); }, { in: { type: 'dip', dur: 0.8, color: '#000' } });
  add(22, (ctx, t, s) => { night(ctx, t); const k = clamp(s.dt / 1.4); if (k < 1) { ctx.save(); ctx.translate(lerp(900, 600, k), FEET - 120); ctx.rotate(-0.4 - k); G.rrect(ctx, -10, -150, 20, 200, 4, { fill: '#9A6A3E', lw: 4, seed: 6400 }); G.rrect(ctx, -30, 40, 60, 16, 4, { fill: '#5A3A22', lw: 3, seed: 6401 }); ctx.restore(); } bob(ctx, { x: 540, r: 84, t, mood: k > 0.8 ? 'chomp' : 'wide' }); }, { cam: C([1.35, 1.42, 0, 200]) });
  add(23, (ctx, t, s) => { night(ctx, t); P(ctx, 'milo', 280, { s: 1.1, mood: 'shock', look: 1 }); bob(ctx, { x: 640, r: 80, t, mood: 'happy' }); stamp(ctx, '...', t, s.t0 + 0.8, { color: '#F6F0E2', y: 700 }); });
  add(24, (ctx, t, s) => { night(ctx, t); bob(ctx, { x: 540, r: 120, t, mood: s.dt > 1.3 ? 'metal' : 'happy' }); if (s.dt > 1.3 && s.dt < 1.5) dim(ctx, 0.0); }, { cam: C([1.6, 1.9, 0, 330]) });
  add(25, (ctx, t, s) => { night(ctx, t); bob(ctx, { x: 540, r: 100, t, mood: 'happy', squash: 0.1 * Math.sin(s.dt * 20) * Math.exp(-s.dt * 3) }); stamp(ctx, '*BURP*', t, s.t0 + 0.3, { color: '#F6F0E2', y: 760, size: 110 }); }, { cam: C([1.4, 1.4, 0, 220]) });
  // the bounty
  add(26, (ctx, t, s) => { square(ctx, t); P(ctx, 'guild', 270, { s: 1.0, gesture: 'point', mood: 'neutral' }); board(ctx, t, s.t0 + 0.3, { title: 'BOUNTY', from: 0, to: 50, d: 1.0, color: '#F2B84B', sub: 'GOLD · RAT KING' }); }, { in: 'fade' });
  add(27, (ctx, t, s) => { sewer(ctx, t, { torch: 0 }); rat(ctx, { x: 520, s: 1.0, t, face: -1 }); sewerLight(ctx, 0.7, 540, 900); tag(ctx, 'RAT KING · LV 12', 520, 640, '#FF6A5A'); stamp(ctx, 'BOSS', t, s.t0 + 0.5, { color: '#FF5A5A' }); }, { in: 'flash', cam: Shots.combine(C([1.0, 1.08]), Shots.shake(16, L(27) + 0.5, 4)) });
  add(28, (ctx, t, s) => { home(ctx, t); table(ctx); P(ctx, 'mom', 240, { s: 1.0, mood: 'happy' }); P(ctx, 'pip', 430, { s: 0.7, mood: 'laugh' }); P(ctx, 'milo', 760, { s: 1.0, face: -1, mood: 'happy' }); counter(ctx, t, s.t0 + 0.3, 'COINS', 3, 53, 1.4); }, { in: 'fade' });
  add(29, (ctx, t, s) => { square(ctx, t, { sx: 940, ss: 0.6 }); P(ctx, 'rolf', 170, { s: 0.95, gesture: 'pointUp', mood: 'smirk' }); drake(ctx, { x: 380, s: 0.8, t }); P(ctx, 'tess', 640, { s: 0.95, mood: 'brave' }); wolf(ctx, { x: 830, s: 0.7, t, face: -1 }); });
  add(30, (ctx, t, s) => { square(ctx, t, { sx: 940, ss: 0.6 }); P(ctx, 'rolf', 280, { s: 1.15, mood: s.dt > 1.2 ? 'smirk' : 'neutral' }); P(ctx, 'milo', 700, { s: 1.1, face: -1, mood: 'brave' }); bob(ctx, { x: 880, r: 40, t }); });
  add(31, (ctx, t, s) => { square(ctx, t, { sx: 940, ss: 0.6 }); P(ctx, 'rolf', 300, { s: 1.2, mood: 'laugh', gesture: 'point' }); P(ctx, 'milo', 760, { s: 1.1, face: -1, mood: 'sad' }); label(ctx, 'ROLE: BAIT', t, s.t0 + 0.9, '#FF6A5A'); }, { cam: C([1.1, 1.18, 0, 120]) });
  add(32, (ctx, t, s) => { home(ctx, t); P(ctx, 'pip', 420, { s: 0.85, mood: 'sad', gesture: 'wave', ribbon: true }); P(ctx, 'milo', 700, { s: 1.15, face: -1, mood: 'happy' }); }, { in: 'fade', cam: C([1.2, 1.3, 0, 150]) });
  // ACT 3: the sewer
  add(33, (ctx, t, s) => { sewer(ctx, t); P(ctx, 'rolf', 170, { s: 0.85, mood: 'smirk' }); drake(ctx, { x: 340, s: 0.65, t }); P(ctx, 'tess', 520, { s: 0.85, mood: 'sad' }); wolf(ctx, { x: 680, s: 0.55, t }); P(ctx, 'milo', 880, { s: 0.85, mood: 'sad', face: -1 }); sewerLight(ctx, 0.9, 400, 800); }, { in: { type: 'dip', dur: 0.8, color: '#000' } });
  add(34, (ctx, t, s) => { sewer(ctx, t); P(ctx, 'milo', 540, { s: 1.2, mood: 'sad', sweat: 0.6 }); for (const [dx, c] of [[-150, '#8E6444'], [150, '#A07548']]) G.rrect(ctx, 540 + dx - 70, 820, 140, 160, 20, { fill: c, lw: 5, seed: 6500 + dx }); bob(ctx, { x: 760, r: 40, t }); sewerLight(ctx, 0.9, 540, 800); label(ctx, 'CARRYING: EVERYTHING', t, s.t0 + 1.2, '#F2B84B'); }, { cam: C([1.2, 1.28, 0, 100]) });
  add(35, (ctx, t, s) => { const fl = s.dt < 1.2 ? (Math.sin(s.dt * 40) > 0 ? 1 : 0.2) : 0.5; sewer(ctx, t); P(ctx, 'milo', 540, { s: 1.15, mood: 'scared' }); sewerLight(ctx, fl, 540, 800); }, { cam: C([1.25, 1.35, 0, 120]) });
  add(36, (ctx, t, s) => { sewer(ctx, t, { torch: 0 }); const br = 0.5 + 0.5 * Math.sin(s.dt * 3); ctx.save(); ctx.globalAlpha = 0.9; for (const sd of [-1, 1]) G.ellipse(ctx, 540 + sd * 70, 720, 18, 12 + br * 4, { fill: '#FF3030', lw: 0, seed: 6600 + sd }); ctx.restore(); sewerLight(ctx, 0.05, 540, 1300); stamp(ctx, '...', t, s.t0 + 0.8, { color: '#F6F0E2', y: 1000 }); });
  add(37, (ctx, t, s) => { sewer(ctx, t); rat(ctx, { x: 640, s: 1.05, t, mouth: 0.5 + 0.3 * Math.sin(s.dt * 8) }); P(ctx, 'milo', 150, { s: 0.9, mood: 'scared' }); sewerLight(ctx, 0.75, 420, 800); hp(ctx, t, 'RAT KING · LV 12', 1); }, { in: 'flash', cam: Shots.combine(C([1.0, 1.05]), Shots.shake(22, L(37), 4)) });
  add(38, (ctx, t, s) => { sewer(ctx, t); drake(ctx, { x: 200, s: 0.9, t }); rat(ctx, { x: 720, s: 0.9, t }); if (s.dt > 0.3 && s.dt < 1.3) { ctx.save(); ctx.globalCompositeOperation = 'screen'; for (let k = 0; k < 8; k++) G.ellipse(ctx, 300 + k * 50, 1080 - Math.sin(k + t * 20) * 20, 30 + k * 6, 22 + k * 3, { fill: k % 2 ? '#FF9A3A' : '#FFD04A', lw: 0, seed: 6700 + k }); ctx.restore(); } sewerLight(ctx, 0.85, 400, 900); hp(ctx, t, 'RAT KING · LV 12', s.dt > 1.0 ? 0.98 : 1); floaty(ctx, t, s.t0 + 1.0, '-3', 720, 800, '#F6F0E2'); });
  add(39, (ctx, t, s) => { sewer(ctx, t); P(ctx, 'tess', 160, { s: 0.95, mood: 'scared' }); const fly = clamp((s.dt - 1.6) / 0.5); wolf(ctx, { x: lerp(420, 120, fly), y: FEET - Math.sin(fly * Math.PI) * 250, s: 0.8, t }); rat(ctx, { x: 790, s: 0.85, t, mouth: s.dt > 1.4 && s.dt < 2 ? 0.7 : 0.2 }); sewerLight(ctx, 0.85, 400, 900); hp(ctx, t, 'RAT KING · LV 12', 0.98); floaty(ctx, t, s.t0 + 1.7, '-80', 300, 900); }, { cam: Shots.combine(C([1.05, 1.1]), Shots.shake(16, L(39) + 1.6, 5)) });
  add(40, (ctx, t, s) => { sewer(ctx, t); P(ctx, 'rolf', 540, { s: 1.5, mood: 'scared', gesture: 'cheer' }); sewerLight(ctx, 0.9, 540, 700); stamp(ctx, 'RUN!', t, s.t0 + 0.6, { color: '#FF5A5A', size: 170 }); }, { cam: C([1.35, 1.45, 0, 220]) });
  add(41, (ctx, t, s) => { sewer(ctx, t); P(ctx, 'rolf', 300, { s: 0.9, face: -1, mood: 'scared', walk: -700, t0: s.t0 }); P(ctx, 'tess', 420, { s: 0.9, face: -1, mood: 'scared', walk: -600, t0: s.t0 + 0.15 }); P(ctx, 'milo', 800, { s: 0.9, face: -1, mood: 'scared', walk: -350, t0: s.t0 + 0.6 }); sewerLight(ctx, 0.9, 400, 800); });
  add(42, (ctx, t, s) => { sewer(ctx, t); const push = clamp((s.dt - 1.4) / 0.25); P(ctx, 'rolf', 330, { s: 1.15, mood: push > 0 ? 'angry' : 'scared', gesture: push > 0 ? 'point' : null }); ctx.save(); ctx.translate(lerp(0, 160, ease.outCubic(push)), 0); ctx.rotate(push * 0.12); P(ctx, 'milo', 600, { s: 1.15, face: -1, mood: push > 0 ? 'shock' : 'scared' }); ctx.restore(); sewerLight(ctx, 0.85, 450, 800); if (push > 0) stamp(ctx, 'SHOVE', t, s.t0 + 1.4, { color: '#FF5A5A', y: 800, size: 100 }); }, { cam: Shots.combine(C([1.2, 1.25, 0, 100]), Shots.shake(14, L(42) + 1.4, 6)) });
  add(43, (ctx, t, s) => { sewer(ctx, t); P(ctx, 'rolf', 540, { s: 1.6, mood: 'smirk', look: 1 }); sewerLight(ctx, 0.8, 540, 700); }, { cam: C([1.5, 1.6, 0, 280]) });
  add(44, (ctx, t, s) => { sewer(ctx, t); P(ctx, 'milo', 540, { s: 1.2, mood: 'shock' }); sewerLight(ctx, 0.7, 540, 800); const k = ease.outBounce(clamp(s.dt / 0.5)); ctx.save(); ctx.translate(0, lerp(-1400, 0, k)); bars(ctx); ctx.restore(); }, { cam: Shots.combine(C([1.0, 1.04]), Shots.shake(18, L(44) + 0.45, 5)) });
  add(45, (ctx, t, s) => { sewer(ctx, t); P(ctx, 'milo', 540, { s: 1.2, mood: 'sad' }); sewerLight(ctx, 0.6, 540, 800); bars(ctx); }, { cam: C([1.05, 1.15, 0, 100]) });
  add(46, (ctx, t, s) => { sewer(ctx, t); P(ctx, 'milo', 150, { s: 0.85, mood: 'scared' }); bob(ctx, { x: 330, r: 44, t, mood: 'sad' }); rat(ctx, { x: 760, s: 0.95, t }); sewerLight(ctx, 0.5, 250, 900); hp(ctx, t, 'RAT KING · LV 12', 0.98); });
  add(47, (ctx, t, s) => { sewer(ctx, t, { torch: lerp(1, 0.3, clamp(s.dt / 1.6)) }); P(ctx, 'milo', 540, { s: 1.2, mood: 'scared' }); sewerLight(ctx, lerp(0.6, 0.15, clamp(s.dt / 1.6)), 540, 800); });
  add(48, (ctx, t, s) => { sewer(ctx, t, { torch: 0.3 }); P(ctx, 'milo', 600, { s: 1.2, mood: 'angry', gesture: s.dt > 1.4 ? 'point' : null, face: -1 }); bob(ctx, { x: 320, r: 50, t, mood: 'sad' }); sewerLight(ctx, 0.25, 500, 850); }, { cam: C([1.15, 1.25, 0, 120]) });
  add(49, (ctx, t, s) => { sewer(ctx, t, { torch: 0.25 }); P(ctx, 'milo', 540, { s: 1.6, mood: 'sad', look: -1 }); sewerLight(ctx, 0.2, 540, 700); }, { cam: C([1.55, 1.7, 0, 300]) });
  add(50, (ctx, t, s) => { sewer(ctx, t, { torch: 0.2 }); rat(ctx, { x: 560, s: 1.5, t, mouth: ease.outCubic(clamp(s.dt / 1.2)) }); sewerLight(ctx, 0.25, 540, 850); }, { cam: Shots.combine(C([1.15, 1.35, 120, 120]), Shots.shake(10, L(50) + 0.3, 3)) });
  add(51, (ctx, t, s) => { sewer(ctx, t, { torch: 0.1 }); P(ctx, 'milo', 540, { s: 1.7, mood: 'sad', eyes: 'closed' }); dim(ctx, clamp(s.dt / 1.2) * 0.95, '0,0,0'); }, { cam: C([1.6, 1.7, 0, 320]) });
  add(52, (ctx, t, s) => { ctx.fillStyle = '#000'; ctx.fillRect(-300, -300, W + 600, H + 600); });
  add(53, (ctx, t, s) => { sewer(ctx, t, { torch: 0.2 }); P(ctx, 'milo', 160, { s: 0.85, mood: 'shock' }); bob(ctx, { x: 400, r: 52, t, mood: 'happy' }); rat(ctx, { x: 790, s: 0.85, t, mouth: 0.8 }); sewerLight(ctx, 0.35, 300, 900); dim(ctx, 0.9 * (1 - clamp(s.dt / 0.8)), '0,0,0'); });
  add(54, (ctx, t, s) => { sewer(ctx, t, { torch: 0.2 }); bob(ctx, { x: 540, r: 90, t, mood: 'happy' }); sewerLight(ctx, 0.5, 540, 900); }, { cam: C([1.4, 1.55, 0, 250]) });
  add(55, (ctx, t, s) => { sewer(ctx, t, { torch: 0.2 }); const j = clamp(s.dt / 0.9); bob(ctx, { x: lerp(330, 640, j), y: FEET - Math.sin(j * Math.PI) * 420, r: lerp(60, 120, j), t, mood: 'chomp', squash: -0.15 }); rat(ctx, { x: 780, s: 0.95, t, mouth: 0.6 }); sewerLight(ctx, 0.45, 540, 800); }, { in: 'whip', cam: C([1.0, 1.08]) });
  add(56, (ctx, t, s) => { sewer(ctx, t, { torch: 0.2 }); const g = clamp((s.dt - 0.3) / 0.35); if (g < 1) rat(ctx, { x: lerp(700, 560, g), s: lerp(0.95, 0.2, g), t, alpha: 1 - g * 0.8, mouth: 0.6 }); bob(ctx, { x: 540, r: g < 1 ? lerp(120, 230, g) : 200 - Math.min(40, (s.dt - 0.65) * 30), t, mood: g < 1 ? 'chomp' : 'happy', squash: g >= 1 ? 0.08 * Math.sin(s.dt * 12) * Math.exp(-(s.dt - 0.65) * 2) : 0 }); sewerLight(ctx, 0.5, 540, 800); hp(ctx, t, 'RAT KING · LV 12', lerp(0.98, 0, g)); stamp(ctx, 'GULP.', t, S.ev.gulp, { size: 170 }); }, { in: 'flash', cam: Shots.combine(C([1.0, 1.04]), Shots.shake(30, S.ev.gulp, 4)) });
  add(57, (ctx, t, s) => { sewer(ctx, t, { torch: 0.2 }); P(ctx, 'milo', 160, { s: 0.85, mood: 'shock' }); bob(ctx, { x: 600, r: 160, t, mood: 'sad' }); sewerLight(ctx, 0.4, 400, 900); });
  // the reveal
  add(58, (ctx, t, s) => { voidBg(ctx, t); bob(ctx, { x: 540, r: 110, t, mood: 'wide', glow: 0.6 }); panel(ctx, t, s.t0 + 1.0, 'SYSTEM', ['Hidden trait unlocked.']); }, { in: { type: 'dip', dur: 0.6, color: '#000' } });
  add(59, (ctx, t, s) => { voidBg(ctx, t); beam(ctx, 540, t, s.t0, '#B98CFF'); bob(ctx, { x: 540, r: 110, t, mood: 'happy', glow: 1 }); card(ctx, t, s.t0 + 0.4, 'BOSS EATER', 'MYTHIC TRAIT', 'absorbs everything it eats'); }, { in: 'flash' });
  add(60, (ctx, t, s) => { voidBg(ctx, t); bob(ctx, { x: 540, r: 120, t, mood: 'happy', glow: 0.7 }); floaty(ctx, t, s.t0 + 0.1, 'BOOTS', 300, 760, '#F6F0E2'); floaty(ctx, t, s.t0 + 0.6, 'DUMMY', 780, 720, '#F6F0E2'); floaty(ctx, t, s.t0 + 1.1, 'SWORD', 380, 660, '#C9D2DE'); floaty(ctx, t, s.t0 + 1.6, '½ TABLE', 720, 640, '#F6F0E2'); });
  add(61, (ctx, t, s) => { voidBg(ctx, t, '#C93F5A'); bob(ctx, { x: 540, r: 130, t, mood: 'wide', glow: 0.9 }); }, { cam: C([1.2, 1.4, 0, 250]) });
  add(62, (ctx, t, s) => { sewer(ctx, t, { torch: 0.3 }); const k = clamp((s.dt - 0.2) / 2.6); const col = k < 0.3 ? BOBG : BOBGRAY; bob(ctx, { x: 540, r: 150, t, col, mood: 'happy', teeth: k > 0.75, eyeCol: k > 0.45 ? REDEYE : INK, glow: 0.5 }); sewerLight(ctx, 0.6, 540, 900); }, { in: 'flash', cam: Shots.combine(C([1.15, 1.3, 0, 180]), Shots.shake(12, L(62) + 0.8, 5)) });
  add(63, (ctx, t, s) => { voidBg(ctx, t, '#C93F5A'); bob2(ctx, { x: 540, r: 120, t, glow: 0.4 }); panel(ctx, t, s.t0 + 0.1, 'SYSTEM', ['Absorbed: RAT KING', 'Skill: PLAGUE BITE (epic)'], { color: '#FF7A8A' }); });
  add(64, (ctx, t, s) => { voidBg(ctx, t, '#F2B84B'); beam(ctx, 540, t, s.t0, '#F2B84B'); const top = bob2(ctx, { x: 540, r: 120, t, glow: 0.3 }); stamp(ctx, '+11 LEVELS', t, s.t0 + 1.3, { size: 110 }); tag(ctx, `BOB · LV ${Math.round(lerp(1, 12, ease.outCubic(clamp((s.dt - 0.3) / 1.6))))}`, 540, top - 50, '#F2B84B'); }, { in: 'flash' });
  add(65, (ctx, t, s) => { voidBg(ctx, t, '#6C3FC9'); bob2(ctx, { x: 540, r: 110, t }); }, { cam: C([1.1, 1.25, 0, 200]) });
  add(66, (ctx, t, s) => { voidBg(ctx, t, '#6C3FC9'); const top = bob2(ctx, { x: 540, r: 110, t }); stamp(ctx, '1 / 100', t, S.ev.counter, { color: '#FFFFFF', y: top - 120, size: 140, rot: 0 }); G.text(ctx, 'BOSSES EATEN', 490, top - 230, { size: 40, align: 'center', fam: 'Bungee', weight: 400, color: '#C9B8F0', alpha: clamp((t - s.t0) / 0.4) }); }, { cam: C([1.0, 1.06]) });
  add(67, (ctx, t, s) => { sewer(ctx, t, { torch: 0.3 }); const k = s.dt > 0.5; if (!k) bars(ctx); bob2(ctx, { x: 540, r: 140, t, mood: 'chomp' }); sewerLight(ctx, 0.6, 540, 900); stamp(ctx, 'CRUNCH', t, S.ev.crunch + 0.5, { color: '#F6F0E2' }); }, { cam: Shots.combine(C([1.0, 1.05]), Shots.shake(24, L(67) + 0.5, 5)) });
  // ACT 4: payoff
  add(68, (ctx, t, s) => { square(ctx, t, { sx: 920, ss: 0.55 }); P(ctx, 'rolf', 260, { s: 1.1, mood: 'sad', gesture: 'shrug' }); P(ctx, 'brann', 560, { s: 0.95, mood: 'sad' }); P(ctx, 'mom', 760, { s: 0.95, face: -1, mood: 'sad' }); P(ctx, 'pip', 900, { s: 0.65, face: -1, mood: 'sad' }); }, { in: 'fade' });
  add(69, (ctx, t, s) => { square(ctx, t, { sx: 920, ss: 0.55 }); P(ctx, 'rolf', 300, { s: 1.2, mood: 'sad', gesture: 'dua' }); P(ctx, 'tess', 740, { s: 1.05, face: -1, mood: 'angry' }); });
  add(70, (ctx, t, s) => { square(ctx, t, { sx: 920, ss: 0.55 }); P(ctx, 'rolf', 220, { s: 1.0, mood: 'shock', look: 1 }); P(ctx, 'brann', 860, { s: 0.95, face: -1, mood: 'shock' }); const sh = Math.sin(s.dt * 40) * 6 * (s.dt < 1 ? 1 : 0); G.ellipse(ctx, 560 + sh, 1230, 130, 34, { fill: '#5E5A52', lw: 6, seed: 6800 }); }, { cam: C([1.1, 1.18, 0, 150]) });
  add(71, (ctx, t, s) => { square(ctx, t, { sx: 920, ss: 0.55 }); beam(ctx, 400, t, s.t0 + 0.6, '#F2B84B'); G.ellipse(ctx, 330, 1250, 130, 30, { fill: '#2A2622', lw: 5, seed: 6801 }); const up = ease.outCubic(clamp(s.dt / 1.0)); P(ctx, 'milo', 400, { s: 1.15, y: FEET + lerp(300, 0, up), mood: 'brave', gesture: 'pointUp' }); G.poly(ctx, [[480, 670 + lerp(300, 0, up)], [560, 670 + lerp(300, 0, up)], [570, 610 + lerp(300, 0, up)], [540, 640 + lerp(300, 0, up)], [520, 600 + lerp(300, 0, up)], [500, 640 + lerp(300, 0, up)], [470, 610 + lerp(300, 0, up)]], { fill: '#F2B84B', lw: 4, seed: 6802, step: 10 }); bob2(ctx, { x: 720, r: 70, t, mood: 'happy' }); }, { cam: C([1.15, 1.2, 0, 120]) });
  add(72, (ctx, t, s) => { square(ctx, t, { sx: 920, ss: 0.55 }); P(ctx, 'rolf', 130, { s: 0.9, mood: 'shock' }); P(ctx, 'kid', 290, { s: 0.8, mood: 'shock' }); P(ctx, 'brann', 760, { s: 0.9, face: -1, mood: 'shock' }); P(ctx, 'mom', 930, { s: 0.9, face: -1, mood: 'shock' }); bob2(ctx, { x: 530, r: 60, t }); });
  add(73, (ctx, t, s) => { square(ctx, t, { sx: 920, ss: 0.55 }); P(ctx, 'rolf', 260, { s: 1.15, mood: 'scared', sweat: 1 }); drake(ctx, { x: 140, s: 0.7, t, face: 1, scared: 1 }); bob2(ctx, { x: 720, r: 80, t, mood: 'happy' }); }, { cam: C([1.15, 1.22, 0, 120]) });
  add(74, (ctx, t, s) => { square(ctx, t, { sx: 920, ss: 0.55 }); beam(ctx, 380, t, s.t0 + 0.2, '#F2B84B'); P(ctx, 'guild', 700, { s: 1.0, face: -1, mood: 'happy' }); P(ctx, 'milo', 380, { s: 1.15, mood: 'happy', gesture: 'cheer' }); counter(ctx, t, s.t0 + 0.2, 'COINS', 3, 53, 1.2); }, { in: 'flash' });
  add(75, (ctx, t, s) => { street(ctx, t); P(ctx, 'tess', 430, { s: 1.1, mood: 'happy', handR: [140, -120], handL: [-20, -120] }); bob2(ctx, { x: 600, r: 70, t, mood: 'happy' }); wolf(ctx, { x: 860, s: 0.75, t, face: -1, happy: 0.9 }); G.rrect(ctx, 810, 1080, 100, 22, 6, { fill: '#F6F0E2', lw: 3, seed: 6900 }); G.heart(ctx, 520, 760 - Math.sin(t * 3) * 14, 1.4); }, { in: 'fade', cam: C([1.15, 1.22, 0, 120]) });
  add(76, (ctx, t, s) => { home(ctx, t); table(ctx); G.ellipse(ctx, 760, 990, 90, 30, { fill: '#B5543C', lw: 4, seed: 6950 }); for (let k = 0; k < 3; k++) { ctx.save(); ctx.globalAlpha = 0.5; G.line(ctx, [[730 + k * 30, 950], [720 + k * 30 + Math.sin(t * 3 + k) * 10, 880], [735 + k * 30, 820]], { color: '#FFFFFF', lw: 5, seed: 6960 + k }); ctx.restore(); } P(ctx, 'mom', 220, { s: 1.0, mood: 'happy' }); P(ctx, 'pip', 420, { s: 0.7, mood: 'laugh' }); P(ctx, 'milo', 560, { s: 1.0, face: -1, mood: 'happy' }); bob2(ctx, { x: 960, r: 50, t, mood: 'happy' }); }, { in: 'fade' });
  add(77, (ctx, t, s) => { home(ctx, t); P(ctx, 'pip', 420, { s: 0.95, mood: 'laugh', gesture: 'cheer', hop: Math.abs(Math.sin(t * 7)) * 30 }); bob2(ctx, { x: 700, r: 70, t, mood: 'happy', squash: 0.1 * Math.sin(t * 14) }); stamp(ctx, 'BOB DAY!', t, s.t0 + 1.0, { size: 120 }); }, { cam: C([1.2, 1.28, 0, 150]) });
  // cliffhanger
  add(78, (ctx, t, s) => { night(ctx, t); const top = bob2(ctx, { x: 540, r: 80, t, mood: 'happy', glow: clamp((s.dt - 2.2) / 0.8) }); tag(ctx, '1 / 100', 540, top - 50, '#F2B84B'); beam(ctx, 540, t, s.t0 + 2.4, '#FF4A5A'); }, { in: { type: 'dip', dur: 1.0, color: '#000' } });
  add(79, (ctx, t, s) => { night(ctx, t); bob2(ctx, { x: 540, r: 80, t, glow: 0.8 }); dim(ctx, 0.3); panel(ctx, t, s.t0 + 0.1, 'SYSTEM', ['Next boss detected.', 'Distance: 200 m'], { color: '#FF7A8A' }); });
  add(80, (ctx, t, s) => { night(ctx, t); P(ctx, 'milo', 330, { s: 1.15, mood: 'scared', look: 1 }); bob2(ctx, { x: 680, r: 60, t }); }, { cam: C([1.2, 1.3, 0, 120]) });
  add(81, (ctx, t, s) => { night(ctx, t, { roofman: [770, 800 + 0 * t] }); dim(ctx, 0.15); }, { cam: (st) => ({ zoom: lerp(1.0, 2.0, ease.inOutCubic(st.u)), x: lerp(0, 230, ease.inOutCubic(st.u)), y: lerp(0, -160, ease.inOutCubic(st.u)) }) });
  add(82, (ctx, t, s) => { night(ctx, t); dim(ctx, 0.35); P(ctx, 'cassian', 540, { s: 1.9, mood: 'smirk', y: 1500 }); }, { cam: C([1.0, 1.1, 0, 0]) });
  add(83, (ctx, t, s) => { voidBg(ctx, t, '#C9283A'); bob2(ctx, { x: 540, r: 90, t, glow: 0.6 }); stamp(ctx, 'BOSS 2 / 100', t, S.ev.found, { color: '#FF5A5A', y: 520, size: 104, rot: 0 }); stamp(ctx, 'FOUND', t, S.ev.found + 0.4, { color: '#FFFFFF', y: 660, size: 90, rot: 0 }); }, { cam: Shots.combine(C([1.0, 1.06]), Shots.shake(20, S.ev.found, 4)) });
  // end card
  SH.push({ at: S.SHOTS[84].t, in: 'fade', cam: null, draw: (ctx, t, s) => {
    ctx.fillStyle = '#1A1426'; ctx.fillRect(0, 0, W, H);
    bob2(ctx, { x: 490, y: 1200, r: 90, t, mood: 'happy', glow: 0.5 });
    const k = ease.outBack(clamp(s.dt / 0.4), 2);
    ctx.save(); ctx.translate(490, 560); ctx.scale(k, k);
    G.text(ctx, 'MY SLIME', 0, -70, { size: 110, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color: '#9EF0B0', stroke: INK, strokeW: 12 });
    G.text(ctx, 'EATS BOSSES', 0, 60, { size: 100, align: 'center', baseline: 'middle', fam: 'Bungee', weight: 400, color: '#F2B84B', stroke: INK, strokeW: 12 });
    ctx.restore();
    if (s.dt > 0.6) { G.text(ctx, 'EPISODE 1', 490, 760, { size: 52, align: 'center', fam: 'Bungee', weight: 400, color: '#F6F0E2' }); G.text(ctx, 'follow for episode 2', 490, 840, { size: 48, align: 'center', fam: 'Patrick Hand', weight: 400, color: '#C9B8F0' }); }
  } });

  const film = Shots.film(SH);
  const subs = S.SUBS.map((l) => ({ ...l }));

  Studio.film({
    post: { vignette: 0.28, grain: 0.05, paper: 0.35 },
    fadeOut: 0.6,
    draw(ctx, t) {
      G.t = t;
      film(ctx, t);
      if (t < S.SHOTS[84].t) Subs.draw(ctx, t, subs, { style: 'pop', size: 62, y: CAPY, maxW: 820, highlight: '#F2B84B' });
    },
  });
})();
