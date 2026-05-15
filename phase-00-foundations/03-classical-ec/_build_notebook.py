"""Build and execute the Phase 0 Hamming-vs-repetition BSC notebook.

Run with::

    uv run python phase-00-foundations/03-classical-ec/_build_notebook.py

The notebook is constructed programmatically with ``nbformat`` so it stays
in lock-step with the promoted ``qec_project.codes.classical`` API, then
executed end-to-end with ``nbclient`` so the saved ``.ipynb`` carries real
cell outputs (the plots and the printed table).
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

NOTEBOOK_PATH = Path(__file__).parent / "hamming_bsc.ipynb"


def build_notebook() -> nbformat.NotebookNode:
    nb = new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {"name": "python"}

    nb.cells.append(
        new_markdown_cell(
            "# Hamming(7,4) vs 3-repetition over the binary symmetric channel\n"
            "\n"
            "This is the Phase 0 capstone notebook for `03-classical-ec`. We\n"
            "compare two of the smallest non-trivial classical codes against a\n"
            "binary symmetric channel (BSC) with flip probability `p`:\n"
            "\n"
            "* **Hamming(7,4)** — rate 4/7, distance 3, corrects one error per\n"
            "  block of 7. We measure a *block* (logical) error: any of the four\n"
            "  decoded message bits disagreeing with what was sent.\n"
            "* **3-repetition** — rate 1/3, distance 3, corrects one error per\n"
            "  block of 3 via majority vote. Logical error: the decoded bit\n"
            "  disagrees with the sent bit.\n"
            "\n"
            "Both have distance 3 so both protect against single-bit errors,\n"
            "but Hamming(7,4) protects four message bits per block while\n"
            "repetition protects only one. The takeaway from the curve below\n"
            "is the relative *block* error: at low `p` Hamming wins comfortably\n"
            "(per-bit rates are similar but Hamming's block packs more bits),\n"
            "while at high `p` the gap narrows. The log-log subplot makes the\n"
            "low-`p` quadratic-in-`p` behaviour visible for both curves —\n"
            "the same characteristic shape we will see again for the rotated\n"
            "surface code in Phase 3."
        )
    )

    nb.cells.append(
        new_code_cell(
            "from __future__ import annotations\n"
            "\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "from qec_project.codes.classical import RepetitionCode, simulate_bsc\n"
            "\n"
            "SEED = 12345\n"
            "N_SHOTS = 50_000\n"
            "P_FLIPS = np.linspace(0.01, 0.30, 10)\n"
            "rep3 = RepetitionCode(n=3)"
        )
    )

    nb.cells.append(
        new_code_cell(
            "p_hamming: list[float] = []\n"
            "p_rep3: list[float] = []\n"
            "for i, p in enumerate(P_FLIPS):\n"
            "    rng_h = np.random.default_rng(SEED + i)\n"
            "    rng_r = np.random.default_rng(SEED + 1000 + i)\n"
            "    p_hamming.append(simulate_bsc(N_SHOTS, float(p), rng_h))\n"
            "    p_rep3.append(rep3.simulate_bsc(N_SHOTS, float(p), rng_r))\n"
            "p_hamming = np.array(p_hamming)\n"
            "p_rep3 = np.array(p_rep3)"
        )
    )

    nb.cells.append(
        new_code_cell(
            "fig, axes = plt.subplots(1, 2, figsize=(11, 4))\n"
            "ax_lin, ax_log = axes\n"
            "ax_lin.plot(P_FLIPS, p_hamming, marker='o', label='Hamming(7,4) block')\n"
            "ax_lin.plot(P_FLIPS, p_rep3, marker='s', label='3-repetition logical')\n"
            "ax_lin.plot(P_FLIPS, P_FLIPS, linestyle=':', color='grey', label='uncoded (y=p)')\n"
            "ax_lin.set_xlabel('BSC flip probability p')\n"
            "ax_lin.set_ylabel('Logical (block) error rate')\n"
            "ax_lin.set_title('Linear scale')\n"
            "ax_lin.legend()\n"
            "ax_lin.grid(True, alpha=0.3)\n"
            "ax_log.loglog(P_FLIPS, p_hamming, marker='o', label='Hamming(7,4) block')\n"
            "ax_log.loglog(P_FLIPS, p_rep3, marker='s', label='3-repetition logical')\n"
            "ax_log.loglog(P_FLIPS, P_FLIPS, linestyle=':', color='grey', label='uncoded (y=p)')\n"
            "ax_log.set_xlabel('BSC flip probability p')\n"
            "ax_log.set_ylabel('Logical error rate')\n"
            "ax_log.set_title('Log-log scale')\n"
            "ax_log.legend()\n"
            "ax_log.grid(True, which='both', alpha=0.3)\n"
            "fig.tight_layout()\n"
            "plt.show()"
        )
    )

    nb.cells.append(
        new_markdown_cell(
            "## Results table\n"
            "\n"
            "All numbers below come from running the simulator above with\n"
            "`SEED = 12345` and `n_shots = 50_000` per point. No values are\n"
            "hand-typed. If Hamming's block-error curve crosses the\n"
            "repetition curve, the crossing `p` is reported."
        )
    )

    nb.cells.append(
        new_code_cell(
            "print(f\"{'p_flip':>10} | {'Hamming(7,4)':>14} | {'3-repetition':>14}\")\n"
            "print('-' * 46)\n"
            "for p, ph, pr in zip(P_FLIPS, p_hamming, p_rep3, strict=True):\n"
            "    print(f'{p:>10.4f} | {ph:>14.5f} | {pr:>14.5f}')\n"
            "\n"
            "diff = p_hamming - p_rep3\n"
            "sign_changes = np.where(np.diff(np.sign(diff)) != 0)[0]\n"
            "if len(sign_changes):\n"
            "    i = int(sign_changes[0])\n"
            "    # Linear interpolation between the two bracketing points.\n"
            "    x0, x1 = P_FLIPS[i], P_FLIPS[i + 1]\n"
            "    y0, y1 = diff[i], diff[i + 1]\n"
            "    crossing = float(x0 - y0 * (x1 - x0) / (y1 - y0))\n"
            "    print(f'\\nCrossing point (Hamming block == repetition logical) near p = {crossing:.4f}')\n"
            "else:\n"
            "    print('\\nNo crossing observed in the swept range.')"
        )
    )

    return nb


def main() -> None:
    nb = build_notebook()
    client = NotebookClient(nb, timeout=120, kernel_name="python3")
    client.execute()
    nbformat.write(nb, NOTEBOOK_PATH)
    print(f"Wrote executed notebook to {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
