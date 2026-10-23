# KNOWN_LIMITATIONS.md — ShorlyNot Framework & App Scope

**VTU-Qiskit Fall Fest 2026 · VTU-QFF-HC-0085**  
**Classification**: Engineering Trade-Offs, Assumptions & Limitations  

---

## 1. Who Gets Blocked: Attribution-Based Response

- **Principle**: the response touches only what the evidence proves. The identity a request *claims* is never punished, because anyone can type a victim's name.
- **Account quarantine** applies only to an account proven by an ML-DSA-44 signature (for example the real signer behind an impersonated bundle).
- **Source quarantine** applies to the request origin (`source_id`) for unauthenticated events (forgery, replay, parameter tampering).
- **Global scope and S4** require evidence the sender cannot forge (measured QBER on the link) or a streak of three attributed violations. Unauthenticated events are capped at S3 with account scope.
- **Recovery**: the stage decays one level per quiet interval (default 300 s, `SHORLYNOT_DECAY_SECONDS`, 0 disables). Quarantines expire when the stage drops below S2. Manual admin reset still exists.
- **Not implemented**: per-source rate limiting, risk scoring by transaction value, and a human approval flow.
- **Audit**: every stage event is appended to a SHA-256 hash chain. Tail truncation is detectable only against an externally anchored head hash.

---

## 2. Real Circuit Signing vs. $\mathcal{O}(n)$ Statevector Verification

- **Sign Path**: Executes real 3-qubit Bell teleportation circuits on `AerSimulator` per check position to generate authentic Bell syndromes $(m_1, m_2)$.
- **Verify Path**: Uses single-qubit projective Born-rule statevector evaluation under depolarizing noise $p_0$.
- **Rationale**: Guarantees sub-millisecond edge router verification throughput ($< 1$ ms) required for real-time banking, while retaining full circuit semantics. Full Aer circuit mode is also selectable (`mode="circuit"`).

---

## 3. Two-Party Profile T1 Scope (Alice Signer, Bob Verifier)

- **Current Architecture**: Focuses on point-to-point payer-to-payee transaction authentication using shared Bell pairs and Pauli corrections.
- **Future Scope**: Three-party arbitrated signatures (Profile T2-AQS) with Trent arbiter or optical multiports for transferable non-repudiation.

---

## 4. PQC Layer (Real ML-KEM-768 and ML-DSA-44, Reference Implementations)

- **Wrap key**: HKDF over the BB84 session key and an ML-KEM-768 (FIPS 203) shared secret. The syndrome bits are protected with AES-256-GCM under that hybrid key.
- **Identity**: each registered key has an ML-DSA-44 (FIPS 204) public key. The bundle header is signed, and verification attributes impersonated bundles to the real signer.
- **Caveats**: `kyber-py` and `dilithium-py` are pure-Python reference implementations and are not constant-time. Swap in liboqs for production. The demo keystore keeps signer secret keys inside the verifier process. BB84 itself is simulated in-process.

---

## 5. Hardware Backends (Qiskit Aer Default, IBM Quantum Optional)

- **Default Engine**: High-fidelity local simulation on Qiskit Aer (`backend="sim"`).
- **IBM Quantum**: Switches gracefully to real IBM QPUs only when `IBM_QUANTUM_TOKEN` is present. Never fakes IBM hardware output.

---
