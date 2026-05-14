"""Noise model constructors.

Built incrementally as the curriculum progresses:
  * Phase 1: independent bit-flip / phase-flip / depolarizing channels.
  * Phase 3: circuit-level depolarizing for surface-code threshold sims.
  * Phase 5: biased noise, SI1000 (superconducting), and leakage augmentation.
"""
