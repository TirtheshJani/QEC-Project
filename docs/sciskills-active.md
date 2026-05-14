# Scientific Agent Skills — active subset for QEC-Project

Upstream: <https://github.com/K-Dense-AI/scientific-agent-skills> (MIT).
Installed via `bash scripts/install_plugins.sh` — **not** vendored. The
catalog ships ~135 skills; only the subset below is in-scope for this
project. Everything else stays dormant.

## Active subset

| Skill | When it fires |
| --- | --- |
| **Paper Lookup** (arXiv / PubMed / bioRxiv) | Capstone lit review; primary arXiv quant-ph access. Single biggest gap in our base toolkit. |
| **BGPT Paper Search** | Structured metadata (methods, sample sizes, quality scores) when bulk-reviewing decoder papers. |
| **Scientific Writing / Peer Review** | Second-opinion review pass independent of ARS. |
| **Matplotlib / Seaborn** | Publication-quality threshold plots and decoder comparison curves. |
| **NetworkX** | Tanner graphs, lattice-surgery diagrams. |
| **scikit-learn + PyTorch Lightning** | Phase 5 neural-decoder branch of the capstone. |
| **SHAP** | Interpret what the neural decoder learned (novelty angle). |
| **PyMC** | Bayesian uncertainty on threshold estimates. |
| **GPU Optimization (CuPy / Numba CUDA)** | Scaling decoder Monte Carlo when CPU caps. |
| **Modal** | Cloud burst for $d \\geq 11$ sweeps; `run_threshold_sweep.py --remote`. |
| **What-If Oracle** | Multi-branch scenario analysis ("which decoder under which noise wins"). |
| **Open Notebook** (optional) | Generate audio summaries of each phase for self-review. |

## Explicitly out of scope (do not pull from the catalog)

BioPython, RDKit, Scanpy, Arboreto, pysam, gget, Datamol, DiffDock, DeepChem,
OpenMM, MDAnalysis, all ClinVar / COSMIC / Reactome / KEGG / STRING /
PrimeKG / DepMap / Clinical Decision Support / PyDESeq2 / PyLabRobot /
Protocols.io / Benchling / LabArchives / DNAnexus / LatchBio / OMERO /
Imaging Data Commons / U.S. Treasury Fiscal Data — none of these are
relevant to QEC.

## Why this list (and not the full 135)

Discovery is fine, but committing to scope is better. Future Claude
sessions should default to one of the skills above; if a request seems to
need a non-listed skill, surface that and ask the user before pulling it
in. Keeps the project on its NRC-decoder mission.
