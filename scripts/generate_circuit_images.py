"""
Generate Publication-Quality Quantum Circuit Diagrams for ShorlyNot-QDS-T1.
Team Momosapiens (VTU-QFF-HC-0085) | VTU-Qiskit Fall Fest 2026.

Outputs high-resolution (300 DPI) circuit diagrams to `docs/circuits/`:
  1. teleportation_circuit_showcase.png  - Annotated 3-qubit teleportation circuit with protocol stages
  2. teleportation_basis_z0.png           - Teleportation of |0> (bit=0, basis=Z)
  3. teleportation_basis_z1.png           - Teleportation of |1> (bit=1, basis=Z)
  4. teleportation_basis_x0.png           - Teleportation of |+> (bit=0, basis=X)
  5. teleportation_basis_x1.png           - Teleportation of |-> (bit=1, basis=X)
  6. teleportation_4states_panel.png      - 2x2 grid comparing all 4 BB84 teleportation states
  7. verification_circuit_honest.png      - Honest Bob verification circuit
  8. verification_circuit_tampered.png    - Residual Pauli discrepancy circuit under syndrome tampering
  9. verification_circuit_forgery.png     - Unentangled forger verification (uncoupled Bell half collapse)
 10. quantum_circuits_composite.png       - Comprehensive multi-panel overview diagram
"""

import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from PIL import Image

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from shorlynot_skeleton.engines.qiskit_aer import QiskitAerEngine

OUTPUT_DIR = ROOT_DIR / "docs" / "circuits"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_annotated_teleportation_circuit(bit: int = 1, basis: int = 1) -> QuantumCircuit:
    """
    Build an annotated 3-qubit teleportation circuit with labeled registers and barriers
    highlighting the stages of ShorlyNot-QDS-T1.
    """
    qr_msg = QuantumRegister(1, name="q_msg (psi)")
    qr_alice = QuantumRegister(1, name="q_alice (A)")
    qr_bob = QuantumRegister(1, name="q_bob (B)")

    cr_m1 = ClassicalRegister(1, name="m1 (Alice Z)")
    cr_m2 = ClassicalRegister(1, name="m2 (Alice X)")
    cr_bob = ClassicalRegister(1, name="c_bob (Verify)")

    qc = QuantumCircuit(qr_msg, qr_alice, qr_bob, cr_m1, cr_m2, cr_bob)

    # 1. State Preparation
    if basis == 0:
        if bit == 1:
            qc.x(qr_msg[0])
    else:
        if bit == 0:
            qc.h(qr_msg[0])
        else:
            qc.x(qr_msg[0])
            qc.h(qr_msg[0])
    qc.barrier(label="1. Prep")

    # 2. Bell State Generation |Phi+>
    qc.h(qr_alice[0])
    qc.cx(qr_alice[0], qr_bob[0])
    qc.barrier(label="2. EPR")

    # 3. Alice Bell State Measurement (BSM)
    qc.cx(qr_msg[0], qr_alice[0])
    qc.h(qr_msg[0])
    qc.measure(qr_msg[0], cr_m1[0])
    qc.measure(qr_alice[0], cr_m2[0])
    qc.barrier(label="3. BSM")

    # 4. Bob Dynamic Pauli Corrections X^m2 Z^m1
    with qc.if_test((cr_m2[0], 1)):
        qc.x(qr_bob[0])
    with qc.if_test((cr_m1[0], 1)):
        qc.z(qr_bob[0])
    qc.barrier(label="4. Pauli Fix")

    # 5. Bob Measurement in designated basis
    if basis == 1:
        qc.h(qr_bob[0])
    qc.measure(qr_bob[0], cr_bob[0])

    return qc


def build_annotated_verification_circuit(
    bit: int,
    basis: int,
    provided_syndrome: tuple[int, int],
    true_syndrome: tuple[int, int] | None = None
) -> QuantumCircuit:
    """
    Build an annotated verification circuit representing either:
      - Honest verification
      - Tampered syndrome verification (with residual Pauli gate injection)
      - Unentangled forgery verification (independent uncoupled Bell state)
    """
    qr_msg = QuantumRegister(1, name="q_msg (psi)")
    qr_alice = QuantumRegister(1, name="q_alice (A)")
    qr_bob = QuantumRegister(1, name="q_bob (B)")

    cr_m1 = ClassicalRegister(1, name="m1 (Alice)")
    cr_m2 = ClassicalRegister(1, name="m2 (Alice)")
    cr_bob = ClassicalRegister(1, name="b' (Bob)")

    qc = QuantumCircuit(qr_msg, qr_alice, qr_bob, cr_m1, cr_m2, cr_bob)

    m1_p, m2_p = provided_syndrome

    if true_syndrome is not None:
        # Message state
        if basis == 0:
            if bit == 1:
                qc.x(qr_msg[0])
        else:
            if bit == 0:
                qc.h(qr_msg[0])
            else:
                qc.x(qr_msg[0])
                qc.h(qr_msg[0])
        qc.barrier(label="1. Prep")

        # Shared Bell Pair
        qc.h(qr_alice[0])
        qc.cx(qr_alice[0], qr_bob[0])
        qc.barrier(label="2. EPR")

        # Alice BSM
        qc.cx(qr_msg[0], qr_alice[0])
        qc.h(qr_msg[0])
        qc.measure(qr_msg[0], cr_m1[0])
        qc.measure(qr_alice[0], cr_m2[0])
        qc.barrier(label="3. BSM")

        # Dynamic Teleportation Recovery
        with qc.if_test((cr_m2[0], 1)):
            qc.x(qr_bob[0])
        with qc.if_test((cr_m1[0], 1)):
            qc.z(qr_bob[0])

        m1_t, m2_t = true_syndrome
        diff_x = m2_t ^ m2_p
        diff_z = m1_t ^ m1_p

        if diff_x == 1 or diff_z == 1:
            qc.barrier(label="Tamper Discrepancy")
            if diff_x == 1:
                qc.x(qr_bob[0])
            if diff_z == 1:
                qc.z(qr_bob[0])
    else:
        # Unentangled adversary
        qc.h(qr_alice[0])
        qc.cx(qr_alice[0], qr_bob[0])
        qc.barrier(label="Uncoupled (rho=I/2)")
        if m2_p == 1:
            qc.x(qr_bob[0])
        if m1_p == 1:
            qc.z(qr_bob[0])

    qc.barrier(label="Bob Measure")
    if basis == 1:
        qc.h(qr_bob[0])
    qc.measure(qr_bob[0], cr_bob[0])

    return qc


def render_and_save(qc: QuantumCircuit, filepath: Path, title: str | None = None, dpi: int = 300) -> None:
    """Render circuit with matplotlib and save at high DPI without horizontal folding."""
    fig = qc.draw(output="mpl", style="iqp", fold=-1)
    if title:
        fig.suptitle(title, fontsize=12, fontweight="bold", y=1.02)
    fig.savefig(filepath, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"  [+] Saved: {filepath.name} ({os.path.getsize(filepath):,} bytes)")


def create_4states_panel() -> None:
    """Create a 2x2 comparison panel of all 4 BB84 teleportation states."""
    img_z0 = Image.open(OUTPUT_DIR / "teleportation_basis_z0.png")
    img_z1 = Image.open(OUTPUT_DIR / "teleportation_basis_z1.png")
    img_x0 = Image.open(OUTPUT_DIR / "teleportation_basis_x0.png")
    img_x1 = Image.open(OUTPUT_DIR / "teleportation_basis_x1.png")

    fig, axes = plt.subplots(2, 2, figsize=(18, 9), constrained_layout=True)

    axes[0, 0].imshow(img_z0)
    axes[0, 0].axis("off")
    axes[0, 0].set_title("(1) Pauli Z Basis |0> State (bit=0, basis=Z)", fontsize=11, fontweight="bold")

    axes[0, 1].imshow(img_z1)
    axes[0, 1].axis("off")
    axes[0, 1].set_title("(2) Pauli Z Basis |1> State (bit=1, basis=Z)", fontsize=11, fontweight="bold")

    axes[1, 0].imshow(img_x0)
    axes[1, 0].axis("off")
    axes[1, 0].set_title("(3) Pauli X Basis |+> State (bit=0, basis=X)", fontsize=11, fontweight="bold")

    axes[1, 1].imshow(img_x1)
    axes[1, 1].axis("off")
    axes[1, 1].set_title("(4) Pauli X Basis |-> State (bit=1, basis=X)", fontsize=11, fontweight="bold")

    panel_path = OUTPUT_DIR / "teleportation_4states_panel.png"
    fig.savefig(panel_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [+] Saved 4-States Panel: {panel_path.name} ({os.path.getsize(panel_path):,} bytes)")


def create_composite_overview() -> None:
    """Combine key circuits into a unified publication-ready figure."""
    img_showcase = Image.open(OUTPUT_DIR / "teleportation_circuit_showcase.png")
    img_honest = Image.open(OUTPUT_DIR / "verification_circuit_honest.png")
    img_forgery = Image.open(OUTPUT_DIR / "verification_circuit_forgery.png")

    fig = plt.figure(figsize=(18, 11), constrained_layout=True)
    gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[1.0, 1.0])

    # Top panel: Full showcase teleportation
    ax_top = fig.add_subplot(gs[0, :])
    ax_top.imshow(img_showcase)
    ax_top.axis("off")
    ax_top.set_title(
        "(A) ShorlyNot-QDS-T1 Teleportation Sign Architecture (Real 3-Qubit AerSimulator Dynamic Circuit)",
        fontsize=13, fontweight="bold", pad=10
    )

    # Bottom left: Honest verification
    ax_bl = fig.add_subplot(gs[1, 0])
    ax_bl.imshow(img_honest)
    ax_bl.axis("off")
    ax_bl.set_title(
        "(B) Honest Entangled Verification Path (P_accept = 1 - p0/2)",
        fontsize=11, fontweight="bold", pad=8
    )

    # Bottom right: Unentangled forgery verification
    ax_br = fig.add_subplot(gs[1, 1])
    ax_br.imshow(img_forgery)
    ax_br.axis("off")
    ax_br.set_title(
        "(C) Adversarial Unentangled Forger (rho_B = I/2 -> 50% Random Collapse)",
        fontsize=11, fontweight="bold", pad=8
    )

    composite_path = OUTPUT_DIR / "quantum_circuits_composite.png"
    fig.savefig(composite_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [+] Saved Composite: {composite_path.name} ({os.path.getsize(composite_path):,} bytes)")


def generate_all_circuits() -> None:
    print("=" * 70)
    print("Generating ShorlyNot Quantum Circuit Diagrams (fold=-1)")
    print("=" * 70)

    # 1. Annotated Showcase Circuit
    showcase_qc = build_annotated_teleportation_circuit(bit=1, basis=1)
    render_and_save(
        showcase_qc,
        OUTPUT_DIR / "teleportation_circuit_showcase.png",
        title="ShorlyNot-QDS-T1: 3-Qubit Bell Teleportation Sign Circuit (|-> state, bit=1, basis=X)"
    )

    # 2. Four BB84 Basis State Teleportation Circuits
    basis_configs = [
        (0, 0, "teleportation_basis_z0.png", "Teleportation Circuit: |0> state (bit=0, basis=Z)"),
        (1, 0, "teleportation_basis_z1.png", "Teleportation Circuit: |1> state (bit=1, basis=Z)"),
        (0, 1, "teleportation_basis_x0.png", "Teleportation Circuit: |+> state (bit=0, basis=X)"),
        (1, 1, "teleportation_basis_x1.png", "Teleportation Circuit: |-> state (bit=1, basis=X)"),
    ]
    for bit, basis, filename, title in basis_configs:
        qc = QiskitAerEngine.build_teleportation_circuit(bit=bit, basis=basis)
        render_and_save(qc, OUTPUT_DIR / filename, title=title)

    # 3. 4-States Panel
    create_4states_panel()

    # 4. Verification Circuits
    # 4A: Honest Entangled Verification
    v_honest = build_annotated_verification_circuit(
        bit=1, basis=1, provided_syndrome=(0, 1), true_syndrome=(0, 1)
    )
    render_and_save(
        v_honest,
        OUTPUT_DIR / "verification_circuit_honest.png",
        title="Bob Projective Verification: Honest Entangled Session (Syndrome Match Δm = 0)"
    )

    # 4B: Tampered Syndrome Verification
    v_tampered = build_annotated_verification_circuit(
        bit=1, basis=1, provided_syndrome=(1, 0), true_syndrome=(0, 1)
    )
    render_and_save(
        v_tampered,
        OUTPUT_DIR / "verification_circuit_tampered.png",
        title="Bob Projective Verification: Tampered Syndrome (Residual Pauli Error X^(Δm2) Z^(Δm1))"
    )

    # 4C: Unentangled Forgery Verification
    v_forgery = build_annotated_verification_circuit(
        bit=1, basis=1, provided_syndrome=(1, 1), true_syndrome=None
    )
    render_and_save(
        v_forgery,
        OUTPUT_DIR / "verification_circuit_forgery.png",
        title="Bob Projective Verification: Unentangled Forger (Maximally Mixed State rho_B = I/2 Collapse)"
    )

    # 5. Multi-Panel Composite Overview
    print("\nCreating Composite Multi-Panel Overview...")
    create_composite_overview()

    print("\n[OK] All quantum circuit diagrams generated successfully in docs/circuits/")


if __name__ == "__main__":
    generate_all_circuits()
