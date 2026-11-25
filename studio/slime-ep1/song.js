// THE SOUNDTRACK for MY SLIME EATS BOSSES ep1: lofi village -> dark sewer -> silence -> orchestral reveal -> warm payoff -> dark hook.
// The narration is the recorded voiceover (vo/NN.wav), placed at each shot's voice time from score.js.
const path = require('path');
const { SR, Bus, reverb } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const Genre = require('./engine/audio/genres');
const U = require('./engine/util');
const MU = require('./engine/music');
const sc = require('./score');
const { DURATION, SHOTS, ev, clock, m } = sc;
const { T, BAR, BEAT } = clock;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const drums = bus(), bass = bus(), pad = bus(), keys = bus(), lead = bus(), fx = bus(), verb = bus(), voice = bus();
const rng = U.mulberry32(11);
const bar = (sec) => Math.floor(sec / BAR);
const L = (i) => SHOTS[i].t;

// ---------- harmony: one chord per bar ----------
const table = {
  C: { notes: ['E4', 'G4', 'C5'], bass: 'C2' }, G: { notes: ['D4', 'G4', 'B4'], bass: 'G1' }, Am: { notes: ['E4', 'A4', 'C5'], bass: 'A1' }, F: { notes: ['F4', 'A4', 'C5'], bass: 'F1' },
  Dm: { notes: ['D4', 'F4', 'A4'], bass: 'D2' }, E: { notes: ['E4', 'G#4', 'B4'], bass: 'E2' }, Bb: { notes: ['D4', 'F4', 'Bb4'], bass: 'Bb1' },
};
const rows = [];
const fill = (b0, b1, prog) => { for (let b = b0, k = 0; b < b1; b++, k++) rows.push([b, 0, 4, prog[k % prog.length]]); };
const nb = Math.ceil(DURATION / BAR) + 1;
fill(0, bar(88.8), ['C', 'G', 'Am', 'F']);
fill(bar(88.8), bar(150.2), ['Am', 'Am', 'Dm', 'E']);
fill(bar(150.2), bar(177.6), ['Am', 'F', 'C', 'G']);
fill(bar(177.6), bar(203.9), ['C', 'F', 'Am', 'G']);
fill(bar(203.9), nb, ['Am', 'Dm', 'Am', 'E']);
const { chordAt } = MU.makeChords(clock, table, rows);
const B = { drums, bass, pad, keys };

// ---------- ACT 1-2: the village (lofi), with a soft start ----------
Genre.play('lofi', { clock, from: 0, to: 2, chordAt, buses: B, gain: 0.6, drums: false });
Genre.play('lofi', { clock, from: 2, to: bar(85.2), chordAt, buses: B, gain: 0.8 });
// the hook on a music box over the opening, later on marimba for the comic bits
const hook = [['E5', 0, 2], ['G5', 2, 1], ['A5', 3, 1], ['G5', 4, 2], ['E5', 6, 1], ['D5', 7, 1]];
const hook2 = [['C5', 0, 2], ['D5', 2, 1], ['E5', 3, 1], ['D5', 4, 3], ['C5', 7, 1]];
const playHook = (b, inst, g, pat) => { for (const [n, s, l] of pat) { const t = clock.T(b, s / 2); lead.addMono(inst(m(n)), t, g); verb.addMono(inst(m(n)), t, g * 0.5); } };
for (let b = 0; b < 4; b++) playHook(b, (n) => I.musicBox(n + 12, { decay: 1.2 }), 0.12, b % 2 ? hook2 : hook);
for (let b = bar(35); b < bar(66); b += 2) playHook(b, (n) => I.marimba(n, { thock: 0.3 }), 0.1, hook);
// comic hits: chomps, misses, gulps, the burp
for (const t of [L(13) + 0.5, L(14) + 0.2, L(14) + 0.9, L(14) + 1.8, L(19) + 0.7]) { fx.addMono(I.pop(0.8), t, 0.5); fx.addMono(I.thud(90, 0.12), t, 0.4); }
for (const t of [L(18) + 0.1, L(18) + 1.0]) fx.addMono(I.boing(), t, 0.35);
fx.addMono(I.bwomp(), L(25) + 0.3, 0.4);
fx.addMono(I.bwomp(), L(11) + 1.8, 0.3);
// the sword hint: a high shimmer
for (let k = 0; k < 6; k++) fx.addMono(I.bell(1800 + k * 220, 0.6, 2, 1.4), L(24) + 1.3 + k * 0.05, 0.05, k % 2 ? 0.4 : -0.4);
// the bounty: a stamp
fx.addMono(I.thud(70, 0.3), L(26) + 0.3, 0.5);
fx.addMono(I.subBoom(0.9, 80, 35), L(27) + 0.5, 0.5);
// Pip's ribbon: the hook alone on a music box, no drums
for (let b = bar(85.2); b < bar(88.8); b++) playHook(b, (n) => I.musicBox(n + 12, { decay: 1.4 }), 0.13, hook2);
Genre.play('lofi', { clock, from: bar(85.2), to: bar(88.8), chordAt, buses: B, gain: 0.5, drums: false });

// ---------- ACT 3: the sewer (dark, no drums) ----------
for (let b = bar(88.8); b < bar(133.9); b++) {
  const c = chordAt(clock.T(b));
  for (const nn of c.notes) { const x = I.padNote(nn - 12, BAR * 1.05, { cutoff: 700, attack: 0.6, release: 0.8 }); pad.addStereo(x.L, x.R, clock.T(b), 0.07); }
  bass.addMono(I.bass(c.bass, BAR * 0.98, { bright: 0.1, sub: 1 }), clock.T(b), 0.35);
}
const hearts = (t0, t1, gap = 0.8, g = 0.5) => { for (let t = t0; t < t1; t += gap) fx.addMono(I.heartbeat(), t, g); };
hearts(L(35), L(37), 0.85, 0.45);
hearts(L(46), L(50), 0.75, 0.5);
hearts(L(50), L(51) + 1.4, 0.5, 0.6);
fx.addMono(I.subBoom(1.2, 70, 30), L(37), 0.7); drums.addMono(I.timpani(m('A1')), L(37), 0.7);
fx.addMono(I.noiseSweep(1.2, 400, 2500, { q: 1 }), L(38) + 0.3, 0.15);
fx.addMono(I.thud(60, 0.4), L(39) + 1.6, 0.6);
fx.addMono(I.thwack(), L(42) + 1.4, 0.6);
fx.addMono(I.thud(50, 0.6), L(44) + 0.45, 0.9); fx.addMono(I.glass(7), L(44) + 0.45, 0.15);
for (let k = 0; k < 7; k++) drums.addMono(I.timpani(m('A1')), L(50) + k * 0.2, 0.1 + k * 0.05);
// silence while his eyes are closed; then the jump
fx.addMono(I.noiseSweep(L(56) + 0.5 - L(55), 200, 5000, { q: 1.5, pink: true, shape: (x) => x * x }), L(55), 0.22);
// GULP
fx.addMono(I.subBoom(1.6, 90, 28), ev.gulp, 0.9);
fx.addMono(I.thud(80, 0.5), ev.gulp, 0.8);
drums.addMono(I.crash(9), ev.gulp, 0.45);
fx.addMono(I.pop(0.5), ev.gulp - 0.05, 0.6);

// ---------- the reveal: orchestral, building ----------
Genre.play('orchestral', { clock, from: bar(150.2), to: bar(161.3), chordAt, buses: B, gain: 0.55, drums: false });
Genre.play('orchestral', { clock, from: bar(161.3), to: bar(176.2), chordAt, buses: B, gain: 0.9 });
for (let k = 0; k < 10; k++) fx.addMono(I.bell(1200 + k * 160, 0.8, 1.5, 1.4), L(59) + 0.35 + k * 0.04, 0.06, (k % 3 - 1) * 0.4);
fx.addMono(I.subBoom(1.0, 90, 40), L(59) + 0.35, 0.5);
for (let k = 0; k < 16; k++) drums.addMono(I.timpani(m('A1')), L(62) + 0.2 + k * 0.15, 0.08 + k * 0.03);
drums.addMono(I.crash(3), L(62) + 2.8, 0.5);
for (const n of ['C4', 'E4', 'G4', 'C5']) { const x = I.brassNote(m(n), 1.2, { bright: 1.2, stab: true, seed: m(n) }); lead.addStereo(x.L, x.R, L(64) + 1.3, 0.12); }
drums.addMono(I.crash(4), L(64) + 1.3, 0.5);
for (let k = 0; k < 11; k++) fx.addMono(I.pop(1 + k * 0.08), L(64) + 0.3 + k * 0.14, 0.18);
fx.addMono(I.subBoom(1.4, 80, 30), ev.counter, 0.8); drums.addMono(I.timpani(m('A1')), ev.counter, 0.8);
// CRUNCH
fx.addMono(I.thwack(), ev.crunch + 0.5, 0.7); fx.addMono(I.glass(5), ev.crunch + 0.5, 0.3); fx.addMono(I.thud(60, 0.4), ev.crunch + 0.5, 0.7);

// ---------- ACT 4: the payoff (warm) ----------
Genre.play('lofi', { clock, from: bar(177.6), to: bar(183.4), chordAt, buses: B, gain: 0.55, drums: false });
fx.addMono(I.subBoom(0.8, 70, 35), L(70), 0.5);
Genre.play('orchestral', { clock, from: bar(184.8), to: bar(198), chordAt, buses: B, gain: 0.8 });
for (const n of ['C4', 'E4', 'G4']) { const x = I.brassNote(m(n), 2.0, { bright: 1.0, seed: m(n) + 3 }); lead.addStereo(x.L, x.R, L(71) + 0.6, 0.1); }
for (let k = 0; k < 8; k++) fx.addMono(I.bell(1400 + k * 200, 0.5, 2, 1.4), L(74) + 0.2 + k * 0.06, 0.06);
Genre.play('lofi', { clock, from: bar(198), to: bar(203.9), chordAt, buses: B, gain: 0.7 });
for (let b = bar(198); b < bar(203.9); b++) playHook(b, (n) => I.musicBox(n + 12, { decay: 1.2 }), 0.1, b % 2 ? hook2 : hook);

// ---------- the hook: dark ----------
for (let b = bar(203.9); b < bar(222.4); b++) {
  const c = chordAt(clock.T(b));
  for (const nn of c.notes) { const x = I.padNote(nn - 12, BAR * 1.05, { cutoff: 800, attack: 0.5, release: 0.8 }); pad.addStereo(x.L, x.R, clock.T(b), 0.07); }
  bass.addMono(I.bass(c.bass, BAR * 0.98, { bright: 0.1, sub: 1 }), clock.T(b), 0.35);
}
hearts(L(78) + 2.2, L(80), 0.8, 0.45);
hearts(L(81), ev.found - 0.2, 0.6, 0.55);
fx.addMono(I.ting(m('E6')), L(79) + 0.1, 0.25);
fx.addMono(I.subBoom(1.8, 90, 28), ev.found, 0.9); drums.addMono(I.timpani(m('A1')), ev.found, 0.9); drums.addMono(I.crash(2), ev.found, 0.4);
// end card: the hook once more
playHook(bar(ev.end) + 1, (n) => I.musicBox(n + 12, { decay: 1.6 }), 0.14, hook);

// ---------- the narration ----------
for (const s of SHOTS) {
  if (s.vo === undefined) continue;
  const v = MIX.loadAudio(path.join(__dirname, 'vo', String(s.i).padStart(2, '0') + '.wav'), { at: s.vo, length: DURATION });
  for (let i = 0; i < N; i++) { voice.L[i] += v.L[i]; voice.R[i] += v.R[i]; }
}

// ---------- mix ----------
const room = reverb(verb, { room: 0.75, damp: 0.4 });
const music = [drums, bass, pad, keys, lead];
for (const b of music.concat([fx])) { MIX.gate(b, L(51) + 0.3, L(53) + 0.2); MIX.gate(b, L(57) + 0.2, L(58) + 0.6); }
MIX.duck(music, voice, { depth: 0.45 });
const stems = { drums, bass, pad, keys, lead, fx, voice, verb: room };
const GAIN = { drums: 0.8, bass: 0.7, pad: 0.9, keys: 0.8, lead: 1.0, fx: 0.9, voice: 2.6, verb: 0.35 };
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? path.join(__dirname, 'out') : null });
MIX.highpass(mix, 30);
MIX.fadeOut(mix, DURATION - 0.8, DURATION);
const res = MIX.master(mix, 0.8, undefined, { lufs: -14 });
MIX.writeWav(path.join(__dirname, 'out', 'music.wav'), mix);
console.log(`out/music.wav ${DURATION.toFixed(1)}s ${res.lufs.toFixed(1)} LUFS`);
