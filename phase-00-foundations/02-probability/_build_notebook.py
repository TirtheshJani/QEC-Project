"""One-shot generator for ``probability.ipynb``.

Run once:

    python -m uv run python phase-00-foundations/02-probability/_build_notebook.py

The notebook is committed; this script exists so the source of truth for
the notebook structure is reviewable in git diff form. It is safe to
re-run: it overwrites the .ipynb file with the regenerated version.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "probability.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


cells: list[nbf.NotebookNode] = []

cells.append(
    md(
        """# Phase 0.2 — Discrete probability and the binary symmetric channel

Second content notebook in the curriculum. Phase 0.1 built the linear
algebra; this one builds the probability and information-theory muscle
that every QEC paper assumes. The final destination is the **binary
symmetric channel** (BSC), the simplest classical noise model, because
Phase 0.3 will encode bits before sending them through that channel
and Phase 3+ will revisit the same picture for the surface code under
bit-flip noise.

We cover, in order:

1. Discrete probability primer (random variables, PMF, expectation,
   variance) with a biased-coin example.
2. Conditional probability and Bayes' rule, with a noisy-channel
   example that previews the BSC.
3. Mutual information `I(X;Y)` from a small joint distribution, by
   hand and numerically.
4. Markov chains: a two-state chain and its stationary distribution.
5. The binary symmetric channel BSC(p) and its Shannon capacity
   `C(p) = 1 - H_2(p)`, plotted across `p`.
6. A Monte Carlo simulation of BSC(p): empirical flip rate versus
   nominal `p`, with the `+/- 1/sqrt(N)` band.

**Helpers used.** `binary_entropy`, `bsc_capacity` from
`qec_project.info`; `bsc_flip` from `qec_project.noise.classical`.
Tests live in `tests/test_info.py` and `tests/test_classical_noise.py`.

**References.** MacKay, *Information Theory, Inference, and Learning
Algorithms*, chapters 1-2 and 9 (BSC); Shannon (1948), the original
capacity paper. Both are in `docs/reading-list.md`.
"""
    )
)

cells.append(
    code(
        """import matplotlib.pyplot as plt
import numpy as np

from qec_project.info import binary_entropy, bsc_capacity
from qec_project.noise.classical import bsc_flip

rng = np.random.default_rng(0)
np.set_printoptions(precision=4, suppress=True)
"""
    )
)

cells.append(
    md(
        """## 1. Discrete probability primer

A **discrete random variable** `X` takes values in a finite (or
countable) **sample space** with a **probability mass function** (PMF)
`p_X(x) = P(X = x)` satisfying `p_X(x) >= 0` and `sum_x p_X(x) = 1`.

For a real-valued `X`,

$$\\mathbb{E}[X] = \\sum_x x \\, p_X(x), \\qquad
\\mathrm{Var}(X) = \\mathbb{E}[(X - \\mathbb{E}[X])^2]
= \\mathbb{E}[X^2] - \\mathbb{E}[X]^2.$$

Concrete example: a biased coin with `P(X=1) = q`, `P(X=0) = 1-q`. Its
expectation is `q` and its variance is `q (1-q)`. Verify by sampling.
"""
    )
)

cells.append(
    code(
        """q = 0.3
n_samples = 100_000
samples = (rng.random(n_samples) < q).astype(np.int8)

empirical_mean = float(samples.mean())
empirical_var = float(samples.var())

print(f"biased coin with q = {q}")
print(f"  E[X] analytic     = {q:.4f}")
print(f"  E[X] empirical    = {empirical_mean:.4f}")
print(f"  Var(X) analytic   = {q * (1 - q):.4f}")
print(f"  Var(X) empirical  = {empirical_var:.4f}")
"""
    )
)

cells.append(
    md(
        """The empirical numbers sit on top of the analytic ones to about three
decimal places at `N = 10^5`, which is the central limit theorem doing
its job: the standard error of the mean is `sqrt(q(1-q)/N) ~ 0.0014`
here, so agreement to ~1e-3 is exactly what we should expect.
"""
    )
)

cells.append(
    md(
        """## 2. Conditional probability and Bayes' rule

For two random variables `X, Y`,

$$P(X = x \\mid Y = y) = \\frac{P(X = x, Y = y)}{P(Y = y)}, \\qquad
P(Y = y) = \\sum_x P(X = x, Y = y).$$

**Bayes' rule** rearranges this into

$$P(X = x \\mid Y = y) = \\frac{P(Y = y \\mid X = x)\\, P(X = x)}{P(Y = y)}.$$

A noisy-channel example that prefigures Section 5: a sender transmits
`X ∈ {0, 1}` with `P(X=0) = P(X=1) = 1/2`. The channel flips the bit
with probability `p = 0.1` and otherwise passes it through. The
receiver observes `Y`. Given `Y = 1`, what was sent?

Forward probabilities:
`P(Y=1 | X=0) = 0.1`, `P(Y=1 | X=1) = 0.9`. Marginal:
`P(Y=1) = 0.5 * 0.1 + 0.5 * 0.9 = 0.5`. Bayes:
`P(X=1 | Y=1) = (0.9 * 0.5) / 0.5 = 0.9`. Confirm numerically.
"""
    )
)

cells.append(
    code(
        """p_flip = 0.1
P_X = np.array([0.5, 0.5])
P_Y_given_X = np.array(
    [
        [1 - p_flip, p_flip],
        [p_flip, 1 - p_flip],
    ]
)

P_joint = P_Y_given_X * P_X[:, None]
P_Y = P_joint.sum(axis=0)
P_X_given_Y = P_joint / P_Y[None, :]

print("Joint P(X, Y) (rows = X, cols = Y):")
print(P_joint)
print(f"Marginal P(Y=1)         = {P_Y[1]:.4f}")
print(f"Posterior P(X=1 | Y=1)  = {P_X_given_Y[1, 1]:.4f}")
print(f"Posterior P(X=0 | Y=1)  = {P_X_given_Y[0, 1]:.4f}")
"""
    )
)

cells.append(
    md(
        """The posterior `P(X=1 | Y=1) = 0.9` is exactly the maximum-a-posteriori
guess a receiver should make on this channel when the prior is uniform.
Phase 0.3's syndrome decoder will compute the same kind of object, just
for a 7-bit codeword instead of a single bit.
"""
    )
)

cells.append(
    md(
        """## 3. Mutual information

The Shannon **entropy** of `X` (in bits, using `log2`) is

$$H(X) = -\\sum_x p_X(x) \\log_2 p_X(x),$$

with the standard `0 log 0 = 0` convention so `H` is continuous at
endpoints. The **joint entropy** and **conditional entropy** are

$$H(X, Y) = -\\sum_{x,y} p(x,y) \\log_2 p(x,y), \\qquad
H(X \\mid Y) = H(X, Y) - H(Y).$$

**Mutual information** measures how much `Y` tells us about `X`:

$$I(X; Y) = H(X) - H(X \\mid Y) = H(Y) - H(Y \\mid X) \\ge 0,$$

with equality to zero iff `X` and `Y` are independent.

For the BSC-with-uniform-prior example above (`p = 0.1`),
`H(X) = 1` bit (uniform binary) and `H(Y|X) = H_2(p) = H_2(0.1)`, so

$$I(X;Y) = 1 - H_2(0.1).$$

That is exactly the BSC capacity formula we will derive in Section 5,
arrived at by a different route. Verify numerically by computing the
joint-distribution form of `I(X;Y)` and the two reformulations
side-by-side.
"""
    )
)

cells.append(
    code(
        """def entropy_bits(probs: np.ndarray) -> float:
    probs = np.asarray(probs, dtype=np.float64).ravel()
    nz = probs[probs > 0]
    return float(-(nz * np.log2(nz)).sum())


joint = P_joint
marginal_X = joint.sum(axis=1)
marginal_Y = joint.sum(axis=0)

H_X = entropy_bits(marginal_X)
H_Y = entropy_bits(marginal_Y)
H_XY = entropy_bits(joint)
H_X_given_Y = H_XY - H_Y
H_Y_given_X = H_XY - H_X

I_from_X = H_X - H_X_given_Y
I_from_Y = H_Y - H_Y_given_X
I_capacity_formula = 1.0 - binary_entropy(p_flip)

print(f"H(X)              = {H_X:.4f}")
print(f"H(Y)              = {H_Y:.4f}")
print(f"H(X | Y)          = {H_X_given_Y:.4f}")
print(f"H(Y | X)          = {H_Y_given_X:.4f}")
print(f"I(X;Y) via H(X) - H(X|Y) = {I_from_X:.4f}")
print(f"I(X;Y) via H(Y) - H(Y|X) = {I_from_Y:.4f}")
print(f"I(X;Y) via 1 - H_2(p)     = {I_capacity_formula:.4f}")
"""
    )
)

cells.append(
    md(
        """All three numbers agree to floating-point precision: the two
reformulations of `I(X;Y)` and the BSC capacity formula are the same
object. This is the seed of the **noisy-channel coding theorem**: the
maximum rate at which information can be reliably transmitted over a
discrete memoryless channel is `max_{p_X} I(X;Y)`, which for the BSC
with uniform input is `1 - H_2(p)`. We will not prove the theorem
here (MacKay Chapter 10 does), but we will plot the capacity in
Section 5.
"""
    )
)

cells.append(
    md(
        """## 4. Markov chains

A discrete-time **Markov chain** on a finite state space is a sequence
`X_0, X_1, X_2, ...` of random variables in which the distribution of
`X_{t+1}` depends only on `X_t` (the **Markov property**, no memory of
earlier states). It is parameterised by a row-stochastic transition
matrix `P` with `P[i, j] = P(X_{t+1} = j | X_t = i)`.

A two-state example: states `0` and `1`, transition probabilities

$$P = \\begin{pmatrix} 0.7 & 0.3 \\\\ 0.4 & 0.6 \\end{pmatrix}.$$

Starting from a distribution `pi_0` (row vector), the distribution at
time `t` is `pi_0 P^t`. The **stationary distribution** `pi^*` solves
`pi^* P = pi^*`, equivalently it is a left eigenvector of `P` with
eigenvalue 1 (equivalently a right eigenvector of `P^T`). For the
matrix above the stationary distribution is `(4/7, 3/7) ~ (0.571,
0.429)`. Verify two ways: iterate `pi_0 P^t` to convergence, and read
the eigenvector off `P^T`.

Why mention Markov chains here? They are the vocabulary for any
*memoryful* channel (e.g. burst-noise models in Phase 4+). The BSC
itself is memoryless and so is a trivial Markov chain on
`{sent_bit_history}` of length 1, but the formalism reappears when we
talk about syndromes evolving over rounds of stabilizer measurement.
"""
    )
)

cells.append(
    code(
        """P_chain = np.array([[0.7, 0.3], [0.4, 0.6]])

pi = np.array([1.0, 0.0])
for _ in range(50):
    pi = pi @ P_chain

vals, vecs = np.linalg.eig(P_chain.T)
idx = int(np.argmin(np.abs(vals - 1.0)))
stationary_eig = vecs[:, idx].real
stationary_eig = stationary_eig / stationary_eig.sum()

print(f"stationary by iteration:        {pi}")
print(f"stationary via eigenvector:     {stationary_eig}")
print(f"analytic (4/7, 3/7):            {np.array([4 / 7, 3 / 7])}")
print("pi @ P == pi (iteration result):", np.allclose(pi @ P_chain, pi))
"""
    )
)

cells.append(
    md(
        """## 5. Binary symmetric channel: definition and capacity

The **binary symmetric channel** `BSC(p)` accepts a bit `X ∈ {0, 1}`
and emits

$$Y = \\begin{cases} X & \\text{with probability } 1 - p, \\\\
1 - X & \\text{with probability } p. \\end{cases}$$

The Shannon capacity of `BSC(p)` is

$$C(p) = 1 - H_2(p), \\qquad H_2(p) = -p \\log_2 p - (1-p) \\log_2(1-p),$$

in bits per channel use, achieved by a uniform input distribution.

* `C(0) = 1`: a noiseless binary channel carries one bit per use.
* `C(0.5) = 0`: a fair-coin channel carries no information; the output
  is independent of the input.
* `C(p) = C(1 - p)`: flipping every bit deterministically is just a
  relabelling, so `p = 0` and `p = 1` are equally informative.

This formula was derived by Shannon (1948); we reuse it via
`qec_project.info.bsc_capacity`. Plot it for `p ∈ [0, 1]`.
"""
    )
)

cells.append(
    code(
        """ps = np.linspace(0.0, 1.0, 401)
caps = bsc_capacity(ps)
ents = binary_entropy(ps)

assert isinstance(caps, np.ndarray)
assert isinstance(ents, np.ndarray)
assert abs(float(caps[0]) - 1.0) < 1e-12
assert abs(float(caps[len(caps) // 2]) - 0.0) < 1e-12

fig, ax = plt.subplots(figsize=(6.0, 4.0))
ax.plot(ps, caps, label="capacity C(p) = 1 - H_2(p)")
ax.plot(ps, ents, label="binary entropy H_2(p)", linestyle="--")
ax.axhline(0, color="black", linewidth=0.5)
ax.axhline(1, color="black", linewidth=0.5)
ax.axvline(0.5, color="gray", linewidth=0.5, linestyle=":")
ax.set_xlabel("flip probability p")
ax.set_ylabel("bits per channel use")
ax.set_title("BSC(p): capacity and binary entropy")
ax.legend(loc="lower center")
ax.set_xlim(0, 1)
ax.set_ylim(-0.05, 1.1)
fig.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        """Sanity-check a few specific values against the formula by hand and
against `qec_project.info`:

* `C(0)   = 1 - H_2(0)   = 1 - 0     = 1.0`
* `C(0.1) = 1 - H_2(0.1) = 1 - 0.469 = 0.531`
* `C(0.5) = 1 - H_2(0.5) = 1 - 1     = 0.0`
"""
    )
)

cells.append(
    code(
        """for p in (0.0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5):
    print(f"p = {p:.2f}  H_2 = {float(binary_entropy(p)):.6f}"
          f"  C = {float(bsc_capacity(p)):.6f}")
"""
    )
)

cells.append(
    md(
        """## 6. Simulating the BSC

Now we *send bits through* a BSC instead of reasoning about its
capacity. For each nominal flip probability `p` in a sweep, draw
`N = 10000` input bits (all zero, since the channel is independent of
the input by the XOR property), pass them through `bsc_flip`, and
count the empirical flip rate. With `N = 10000` the one-sigma Bernoulli
standard error is `sqrt(p(1-p)/N)`, which is bounded above by
`1/(2 sqrt(N)) ~ 0.005`. We plot a `+/- 1/sqrt(N) ~ 0.01` band, which
is roughly two sigma at `p = 0.5` and looser at the endpoints.
"""
    )
)

cells.append(
    code(
        """nominal_ps = np.array([0.0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5])
n_bits = 10_000

empirical_ps = np.empty_like(nominal_ps)
for i, p in enumerate(nominal_ps):
    bits = np.zeros(n_bits, dtype=np.uint8)
    received = bsc_flip(bits, float(p), rng)
    empirical_ps[i] = float(received.mean())

band = 1.0 / np.sqrt(n_bits)

print(f"{'p_nominal':>10} {'p_empirical':>12} {'|diff|':>10}")
for p, emp in zip(nominal_ps, empirical_ps, strict=True):
    print(f"{p:>10.4f} {emp:>12.4f} {abs(emp - p):>10.4f}")
print(f"\\n+/- 1/sqrt(N) band = +/- {band:.4f}")
"""
    )
)

cells.append(
    code(
        """fig, ax = plt.subplots(figsize=(6.0, 4.0))
ax.plot([0, 0.5], [0, 0.5], color="gray", linestyle="--", label="ideal y = p")
ax.fill_between(
    [0, 0.5],
    [-band, 0.5 - band],
    [band, 0.5 + band],
    color="gray",
    alpha=0.15,
    label=f"+/- 1/sqrt(N), N = {n_bits}",
)
ax.scatter(nominal_ps, empirical_ps, zorder=3, label="empirical")
ax.set_xlabel("nominal flip probability p")
ax.set_ylabel("empirical flip rate")
ax.set_title("BSC simulation: empirical vs nominal flip rate")
ax.legend(loc="upper left")
ax.set_xlim(-0.02, 0.52)
ax.set_ylim(-0.02, 0.55)
fig.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        """Every dot lands inside the `+/- 1/sqrt(N)` band: the BSC simulator is
behaving exactly as advertised. The diagonal *is* the channel's
behaviour, because we drew all-zero inputs and any flipped bit becomes
a one. With a non-trivial input distribution we would instead measure
the empirical *disagreement* between sent and received bits, which is
the same number by the XOR property tested in
`tests/test_classical_noise.py::test_bsc_flip_xor_property`.

## Recap and next steps

What we now have in hand:

* A working vocabulary for discrete probability: PMF, expectation,
  variance, conditional probability, Bayes, joint distributions.
* `I(X;Y)` computed three ways for the BSC-with-uniform-prior
  example, all agreeing — and matching the capacity formula
  `C(p) = 1 - H_2(p)`.
* A two-state Markov chain with its stationary distribution computed
  two ways; the formalism we will reuse for memoryful channels.
* The BSC defined and its capacity plotted; a Monte Carlo simulation
  showing empirical flip rates inside the `+/- 1/sqrt(N)` band.

**Foreshadowing Phase 0.3.** In the next notebook we will encode each
information bit redundantly with a Hamming(7,4) code, send those
codewords through the same `bsc_flip`, decode the output via the
syndrome rule, and plot the **logical** error rate vs `p`. The gap
between the diagonal `y = p` plotted here and the new curve there will
be the first error-correction win we measure with our own hands.

**Next deliverable:** Phase 0.3 — classical error correction
(`phase-00-foundations/03-classical-ec/`).
"""
    )
)


nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.12",
    },
}

OUT.write_text(nbf.writes(nb), encoding="utf-8")
print(f"wrote {OUT}")
