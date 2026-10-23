"""
Unified CLI & Evaluation Entry Point (`python -m src.main`) for ShorlyNot.
Team Momosapiens (VTU-QFF-HC-0085) — VTU-Qiskit Fall Fest 2026.

Usage:
  python -m src.main           # Run full Qiskit Aer QDS-T1 + Q-STDF verification suite
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shorlynot_skeleton.detect.tau import TauCalculator
from shorlynot_skeleton.engines.qiskit_aer import QiskitAerEngine
from shorlynot_skeleton.qds.protocol import QdsT1Protocol


def run_quantum_core_showcase() -> None:
    print("=" * 78)
    print("  SHORLYNOT — TELEPORTATION-ASSISTED QDS (ShorlyNot-QDS-T1) & Q-STDF ENGINE")
    print("  Team Momosapiens (VTU-QFF-HC-0085) | VTU-Qiskit Fall Fest 2026 | Qiskit Aer")
    print("=" * 78)

    qc = QiskitAerEngine.build_teleportation_circuit(bit=1, basis=1)
    op_counts = dict(qc.count_ops())
    print("\n[1] 3-Qubit Qiskit Teleportation Circuit Inspection (Qiskit AerSimulator)")
    print(f"    Qubits: {qc.num_qubits} | Classical Bits: {qc.num_clbits} | Depth: {qc.depth()} | Ops: {op_counts}")

    proto = QdsT1Protocol(p0=0.02, default_delta=0.01)
    digest = hashlib.sha256(b"alice->bob:INR:5000:tx-vtu-qff-0085").hexdigest()

    t0 = time.perf_counter()
    bundle = proto.sign(payload_hash=digest, key_id="alice-key-1", n_checks=64, L=128)
    sign_ms = (time.perf_counter() - t0) * 1000.0

    v_analytic = proto.verify(bundle, verifier_id="bob", mode="analytic")
    v_circuit = proto.verify(bundle, verifier_id="bob", mode="circuit")

    print(f"    Sign (64 real Qiskit Aer circuits) : {sign_ms:.2f} ms")
    print(
        f"    Verify [Analytic Born-rule O(n)]   : {v_analytic.verification_time_ms:.3f} ms "
        f"| Accepted={v_analytic.candidate_accepted} (p_hat={v_analytic.mismatch_rate:.4f} <= tau={v_analytic.tau:.4f})"
    )
    print(
        f"    Verify [Full AerSimulator Circuit] : {v_circuit.verification_time_ms:.2f} ms "
        f"| Accepted={v_circuit.candidate_accepted} (p_hat={v_circuit.mismatch_rate:.4f} <= tau={v_circuit.tau:.4f})"
    )

    print("\n[2] Classical Baseline vs. ShorlyNot Hybrid Quantum-PQC Architecture")
    print("-" * 78)
    print(f"  {'Capability / Metric':<34} | {'Classical ECDSA + ML IDS':<20} | {'ShorlyNot (QDS + PQC)'}")
    print("-" * 78)
    rows = [
        ("Shor / Quantum Key-Recovery Risk", "Vulnerable (ECDSA)", "Protected (ML-DSA-44 + KEM-768)"),
        ("Passive Channel Tap Detection", "Undetectable", "Detected via QBER >= 11% (BB84)"),
        ("Unentangled Forgery Bound (n=64)", "N/A (Math hardness)", "P_forge = 9.40e-07 (Binomial)"),
        ("Unentangled Forgery Bound (n=128)", "N/A (Math hardness)", "P_forge = 7.78e-17 (Binomial)"),
        ("Anomaly Detector Explainability", "Opaque / Drift-prone", "Exact Hoeffding Bound (No ML)"),
        ("False-Flag Victim Lockout (DoS)", "Locks named account", "Attribution-scoped (Alice safe)"),
        ("Gateway Verification Latency", "~0.5 - 2.0 ms", f"{v_analytic.verification_time_ms:.3f} ms (O(n) Born-rule)"),
    ]
    for metric, classical, quantum in rows:
        print(f"  {metric:<34} | {classical:<20} | {quantum}")
    print("-" * 78)

    print("\n[3] Theoretical Forgery Bounds Across Check Bit Budgets (Aer Noise Floor p0=0.02, delta=0.01)")
    for n_val in (32, 64, 128):
        tau_val = TauCalculator.calculate_tau(p0=0.02, delta=0.01, n=n_val)
        p_forge = TauCalculator.calculate_theoretical_p_forge(tau=tau_val, n=n_val)
        print(f"    n = {n_val:<3} | Hoeffding tau = {tau_val:.4f} | Exact Binomial P_forge = {p_forge:.3e}")

    print("\n[4] Running Live 8-Step Attack & Defense Verification Suite...\n")
    from scripts.demo_attacks import run_attack_demonstration

    if not run_attack_demonstration():
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="ShorlyNot Runner (VTU-QFF-HC-0085)")
    parser.parse_args()
    run_quantum_core_showcase()


if __name__ == "__main__":
    main()
