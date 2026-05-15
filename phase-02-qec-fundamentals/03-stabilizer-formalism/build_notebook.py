"""Build and execute the stabilizer-formalism notebook programmatically.

This script is the source of truth for ``stabilizers.ipynb``: rerun it
whenever the Steane construction or the Pauli API changes.
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = Path(__file__).parent
NB_PATH = HERE / "stabilizers.ipynb"


def build() -> nbformat.NotebookNode:
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(
            "# Stabilizer formalism: the Steane $[[7,1,3]]$ code\n"
            "\n"
            "We use the symplectic Pauli implementation in "
            "`qec_project.codes.pauli` and the Steane construction in "
            "`qec_project.codes.steane` to inspect stabilizers, logical "
            "operators, and a handful of error syndromes."
        ),
        new_code_cell(
            "from qec_project.codes.pauli import Pauli, commutes_with_set\n"
            "from qec_project.codes.steane import (\n"
            "    steane_logical_x,\n"
            "    steane_logical_z,\n"
            "    steane_stabilizers,\n"
            "    verify_steane,\n"
            ")\n"
            "\n"
            "print('verify_steane():', verify_steane())"
        ),
        new_markdown_cell(
            "## Stabilizer table\n"
            "\n"
            "Three X-type and three Z-type generators, each of weight 4."
        ),
        new_code_cell(
            "stabs = steane_stabilizers()\n"
            "header = f\"{'idx':>3} | {'type':>4} | {'operator':>10} | {'wt':>2}\"\n"
            "print(header)\n"
            "print('-' * len(header))\n"
            "for i, s in enumerate(stabs):\n"
            "    kind = 'X' if s.x.any() else 'Z'\n"
            "    print(f'{i:>3} | {kind:>4} | {s.to_string():>10} | {s.weight():>2}')"
        ),
        new_markdown_cell(
            "## Logical operators\n"
            "\n"
            "`X_L` and `Z_L` each have weight 3 (a minimum-weight "
            "representative within their coset of the stabilizer group), "
            "and they anti-commute."
        ),
        new_code_cell(
            "lx = steane_logical_x()\n"
            "lz = steane_logical_z()\n"
            "print('X_L =', lx.to_string(), '  weight', lx.weight())\n"
            "print('Z_L =', lz.to_string(), '  weight', lz.weight())\n"
            "print('[X_L, Z_L] commute?', lx.commutes_with(lz))"
        ),
        new_markdown_cell(
            "## Syndromes of a few sample errors\n"
            "\n"
            "Each row records which of the six stabilizers anti-commutes "
            "with the error (a `1` means the stabilizer flags the error)."
        ),
        new_code_cell(
            "samples = [\n"
            "    'IIIIIII',  # no error\n"
            "    'XIIIIII',  # single X on qubit 0\n"
            "    'IZIIIII',  # single Z on qubit 1\n"
            "    'IIYIIII',  # single Y on qubit 2\n"
            "    'XIZIIII',  # X on 0, Z on 2 (two-qubit)\n"
            "    'IIIIIYI',  # single Y near the end\n"
            "]\n"
            "labels = [f'S{i}' for i in range(len(stabs))]\n"
            "print('error    | ' + ' '.join(labels))\n"
            "print('-' * (11 + 3 * len(labels)))\n"
            "for s in samples:\n"
            "    err = Pauli.from_string(s)\n"
            "    bits = [0 if err.commutes_with(g) else 1 for g in stabs]\n"
            "    print(f'{s} | ' + '  '.join(str(b) for b in bits))\n"
            "print()\n"
            "print('All sample errors detected by at least one stabilizer?')\n"
            "non_trivial = [Pauli.from_string(s) for s in samples if any(ch != 'I' for ch in s)]\n"
            "print(all(not commutes_with_set(e, stabs) for e in non_trivial))"
        ),
        new_markdown_cell(
            "## Observation\n"
            "\n"
            "Every weight-1 and weight-2 Pauli on seven qubits triggers at "
            "least one stabilizer, which is the algebraic statement that "
            "Steane has distance 3. The logical operators sit at exactly "
            "that minimum weight."
        ),
    ]
    return nb


def main() -> None:
    nb = build()
    client = NotebookClient(nb, timeout=120, kernel_name="python3")
    client.execute()
    nbformat.write(nb, NB_PATH)
    print(f"wrote {NB_PATH}")


if __name__ == "__main__":
    main()
