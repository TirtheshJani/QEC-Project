# 11 — The surface code (intro)

The leading candidate for fault-tolerant quantum computing on real hardware. Originally Kitaev's *toric code* (2003), adapted to a flat planar lattice as the *surface code* (Bravyi & Kitaev 1998; Dennis–Kitaev–Landahl–Preskill 2002; Fowler et al. 2012). It is a CSS stabilizer code with three killer features:

1. **2D locality.** Every stabilizer involves at most four data qubits, all geometric nearest neighbours. This matches almost every realistic qubit hardware (planar superconducting, silicon dot, neutral atom).
2. **High threshold.** Around `1%` for circuit-level depolarising noise — two orders of magnitude better than concatenated Steane.
3. **Polynomial logical-error suppression.** Logical error rate scales as `(p / p_th)^{(d+1)/2}` with code distance `d`. Doubling distance squares the error rate (roughly).

These three properties together make the surface code the **only** code that's currently being seriously engineered for fault-tolerant hardware.

This note is a conceptual introduction with a tiny implementation. We do not build a decoder; the standard decoder is **MWPM** (minimum-weight perfect matching), and a competent implementation needs PyMatching or Stim, which are out of scope here.

## The lattice

Consider data qubits on a `d × d` grid (the **rotated** surface code; Fowler et al.). For `d = 3`:
```
qubit (r, c)  ->   index r*3 + c
0  1  2
3  4  5
6  7  8
```
Stabilizers are placed on the *faces* and *edges* of this grid:

- **Bulk plaquettes** (4 of them for `d = 3`): each is a 4-qubit face. They alternate X-type and Z-type in a checkerboard.
- **Boundary plaquettes** (4 of them for `d = 3`, 2 X + 2 Z): weight-2 operators glued to each edge of the lattice.

Total: `d^2 - 1` stabilizer generators on `d^2` data qubits → 1 logical qubit.

The shape of the boundary is what gives the code its logical operators. Because the top/bottom edges have one stabilizer type and the left/right edges have the other, **strings of Pauli operators that traverse the lattice horizontally or vertically** form the non-stabilizer logical operators.

## Stabilizers and logicals

For `d = 3`, the stabilizers our `qec.codes.surface.SurfaceCode(3)` builds are:
- 4 X-type plaquettes
- 4 Z-type plaquettes
(see `demos/08_surface_code_intro.ipynb` for the strings)

The logical operators have **weight `d`**:
- Logical X is an `X` string on a single row (e.g. the top row): weight 3 for `d = 3`.
- Logical Z is a `Z` string on a single column (e.g. the leftmost): weight 3 for `d = 3`.

These two strings cross at exactly one qubit (the corner) and so anticommute (logical X and logical Z must), and each commutes with every stabilizer because any plaquette either misses the string entirely or shares an even number of qubits with it.

Distance `d` against arbitrary Pauli noise: the minimum-weight non-trivial coset representative is `d` (the length of a shortest string from one boundary to the matching boundary).

## Syndrome and error chains

When a Pauli error `E` hits one or more data qubits, the stabilizer generators it anticommutes with light up — these are the **syndrome bits** or **detection events**. For a surface code, the geometry of detection events tells you a lot:

- A single `Z` error on qubit `q` flips exactly the X-stabilizers adjacent to `q`. In the bulk, that's 2 stabilizers; on a boundary, just 1.
- Two `Z` errors on adjacent qubits flip 4 X-stabilizers (or 2 if they share one), which can be re-described as a *path* of length 2 between the syndrome bits.
- A whole *string* of `Z` errors flips only the X-stabilizers at its endpoints. Strings of length up to `(d - 1) / 2` can be safely corrected; strings of length `d` form a logical Z.

This is why the surface-code decoding problem reduces to **matching pairs of detection events to error chains**: every syndrome configuration is the boundary of some Z-error chain (and dually for X errors), and we want the lowest-weight chain that produces it.

## MWPM decoding (the high-level idea)

The decoder is **minimum-weight perfect matching** on a graph whose vertices are detection events (and "boundary" pseudo-vertices for unpaired events) and whose edges are weighted by the most-likely error chain connecting them.

For independent Pauli noise, this is provably optimal up to constant factors. PyMatching implements MWPM at billions-of-qubits-per-second scale via Blossom. We do not implement it here; running real surface-code experiments is a follow-on.

## Threshold

The number that gets quoted: `p_th ≈ 1%` for circuit-level depolarising noise with the standard syndrome-extraction circuits and MWPM decoding. The key data point you'll see plotted in any surface-code paper is `P_L vs p` for several `d` values: below threshold the curves separate (`P_L` decreases with `d`); above threshold they collapse (more code makes things worse). The intersection point is the threshold.

For independent depolarising noise (no measurement errors), the threshold is closer to `~10%`. The drop from `10%` to `1%` is the cost of realistic syndrome-extraction circuits — every CNOT can fail, every measurement can fail.

## Why we stop here

The surface code is a deep topic — fault-tolerant logical gates (lattice surgery, code deformation, twist defects), magic state distillation factories built on the surface code, the actual numerical thresholds and optimal decoders, decoding under measurement noise, etc. — and the project plan stops at the conceptual introduction.

If you ever want to pick this up:
1. Stim (Gidney et al.) for fast circuit-level Pauli sampling.
2. PyMatching for MWPM decoding.
3. Fowler et al. 2012 (https://arxiv.org/abs/1208.0928) is the practical-engineering reference.
4. Litinski 2019 (https://arxiv.org/abs/1808.02892) is the standard primer on lattice surgery.
5. Roffe 2019 (https://arxiv.org/abs/1907.11157) is a good top-down review.

## Demo

`demos/08_surface_code_intro.ipynb`:
- Build a `d = 3` surface code; print the stabilizers and visualise them on the lattice.
- Inject a single `Z` error on a data qubit and read off the syndrome (two adjacent X-stabilizers flip).
- Inject a chain of three `Z` errors spanning the lattice — observe that this is a logical Z (no syndrome events, but the encoded state is now logically flipped).
- Repeat for `d = 5` to show how the lattice scales.
