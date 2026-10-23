# ShorlyNot Skeleton

The core quantum digital signature simulation engine and threat classifier for ShorlyNot.

## Package Structure

- `shorlynot_skeleton.qds`: ShorlyNot-QDS-T1 protocol implementation, Bell state preparation, Pauli eigenstate encoding, syndrome extraction, and entanglement session management.
- `shorlynot_skeleton.detect`: Q-STDF non-ML threat classification engine using Hoeffding bounds (`tau.py`) and a deterministic decision ladder (`classifier.py`).
- `shorlynot_skeleton.stages`: Security stage state machine ($S_0 \to S_4$ for transaction authorization, $Q_0 \to Q_4$ for key exchange health).
- `shorlynot_skeleton.qkd`: BB84 quantum key distribution simulation with physical Eve interception and channel QBER monitoring.
- `shorlynot_skeleton.pqc`: Symmetric payload encryption (AES-256-GCM) and key encapsulation adapters.
- `shorlynot_skeleton.attacks`: Executable attack generators (forgery, impersonation, replay, unauthorized verification, channel tampering, parameter downgrade, and payload tampering).
- `shorlynot_skeleton.engines`: Qiskit Aer and PennyLane circuit execution backends.

## Installation

```bash
cd skeleton
pip install -e .
```

## Running Tests

```bash
pytest
```
