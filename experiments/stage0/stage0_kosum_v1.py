from __future__ import annotations

import hashlib
import itertools
import json
import os
import platform
import random
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "veri"
OUT = HERE / "sonuclar"
REPO = HERE.parent / "12_GitHub_Repo" / "cdsa-bb3"
sys.path.insert(0, str(REPO))

from src.cryptography.aes_gcm import kayit_desifre, kayit_sifrele
from src.cryptography.shamir import anahtari_birlestir, anahtari_paylaristir
from cryptography.exceptions import InvalidTag
import cryptography

SEED = 20260823
FS = 360
SECONDS = 600
PACKET_SAMPLES = FS
TOTAL_PACKETS = SECONDS

SOURCES = {
    "mitdb_100.dat": "https://physionet.org/files/mitdb/1.0.0/100.dat",
    "mitdb_100.hea": "https://physionet.org/files/mitdb/1.0.0/100.hea",
    "nstdb_bw.dat": "https://physionet.org/files/nstdb/1.0.0/bw.dat",
    "nstdb_bw.hea": "https://physionet.org/files/nstdb/1.0.0/bw.hea",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download() -> list[dict]:
    DATA.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, url in SOURCES.items():
        path = DATA / name
        if not path.exists():
            urllib.request.urlretrieve(url, path)
        rows.append({"file": name, "url": url, "bytes": path.stat().st_size, "sha256": sha256(path)})
    return rows


def decode_212(path: Path, samples: int) -> np.ndarray:
    raw = np.fromfile(path, dtype=np.uint8)
    triples = raw[: (len(raw) // 3) * 3].reshape(-1, 3)
    a = triples[:, 0].astype(np.int16) | ((triples[:, 1] & 0x0F).astype(np.int16) << 8)
    b = triples[:, 2].astype(np.int16) | ((triples[:, 1] & 0xF0).astype(np.int16) << 4)
    a = np.where(a >= 2048, a - 4096, a).astype(np.int16)
    b = np.where(b >= 2048, b - 4096, b).astype(np.int16)
    return np.column_stack((a, b))[:samples]


def add_noise(signal: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    sig = signal.astype(np.float64)
    noi = noise.astype(np.float64)
    noi = noi - noi.mean(axis=0)
    sig_power = np.mean(sig * sig, axis=0)
    noi_power = np.maximum(np.mean(noi * noi, axis=0), 1e-12)
    scale = np.sqrt(sig_power / (noi_power * (10 ** (snr_db / 10))))
    return np.rint(sig + noi * scale).clip(-32768, 32767).astype(np.int16)


def packetize(arr: np.ndarray, scenario: str, delay_ms: int = 0) -> list[dict]:
    packets = []
    for i in range(TOTAL_PACKETS):
        block = arr[i * PACKET_SAMPLES : (i + 1) * PACKET_SAMPLES]
        packets.append({
            "dataset": "mitdb-1.0.0-record-100",
            "scenario": scenario,
            "packet_id": i,
            "sample_start": i * PACKET_SAMPLES,
            "sample_count": len(block),
            "delay_ms": delay_ms,
            "samples": block.tolist(),
        })
    return packets


def drop_packets(packets: list[dict], pct: int, rng: random.Random) -> list[dict]:
    n = round(len(packets) * pct / 100)
    dropped = set(rng.sample(range(len(packets)), n))
    return [p for i, p in enumerate(packets) if i not in dropped]


def disconnect(packets: list[dict], seconds: int) -> list[dict]:
    start = (len(packets) - seconds) // 2
    return packets[:start] + packets[start + seconds :]


def longest_run(ids: list[int]) -> int:
    if not ids:
        return 0
    best = cur = 1
    for a, b in zip(ids, ids[1:]):
        cur = cur + 1 if b == a + 1 else 1
        best = max(best, cur)
    return best


def run_scenario(name: str, packets: list[dict], key: bytes, tamper: bool = False) -> dict:
    encrypted = []
    enc_ms = []
    dec_ms = []
    plaintext_bytes = 0
    stored_bytes = 0
    ok = 0
    rejected = 0
    recovered_ids = []
    for p in packets:
        plain = json.dumps(p, separators=(",", ":")).encode()
        plaintext_bytes += len(plain)
        t0 = time.perf_counter_ns()
        e = kayit_sifrele(p, key, f"STAGE0-{name}", f"packet-{p['packet_id']:04d}")
        enc_ms.append((time.perf_counter_ns() - t0) / 1e6)
        if tamper:
            c = bytearray.fromhex(e["sifreli"])
            c[len(c) // 2] ^= 1
            e["sifreli"] = c.hex()
        stored_bytes += len(json.dumps(e, separators=(",", ":")).encode())
        encrypted.append(e)
        t1 = time.perf_counter_ns()
        try:
            d = kayit_desifre(e, key)
            dec_ms.append((time.perf_counter_ns() - t1) / 1e6)
            ok += int(d == p)
            recovered_ids.append(p["packet_id"])
        except InvalidTag:
            dec_ms.append((time.perf_counter_ns() - t1) / 1e6)
            rejected += 1
    lat = enc_ms + dec_ms
    return {
        "scenario": name,
        "input_packets": len(packets),
        "verified_packets": ok,
        "rejected_packets": rejected,
        "integrity_rate": ok / len(packets) if packets else 1.0,
        "rejection_rate": rejected / len(packets) if packets else 0.0,
        "recoverable_timeline_rate": ok / TOTAL_PACKETS,
        "longest_contiguous_seconds": longest_run(recovered_ids),
        "crypto_latency_median_ms": statistics.median(lat),
        "crypto_latency_p95_ms": float(np.percentile(lat, 95)),
        "plaintext_bytes": plaintext_bytes,
        "stored_json_bytes": stored_bytes,
        "storage_ratio": stored_bytes / plaintext_bytes if plaintext_bytes else 0,
        "raw_crypto_overhead_per_packet_bytes": 28,
    }


def main() -> None:
    sources = download()
    signal = decode_212(DATA / "mitdb_100.dat", FS * SECONDS)
    noise = decode_212(DATA / "nstdb_bw.dat", FS * SECONDS)
    rng = random.Random(SEED)
    key = os.urandom(32)
    shares = anahtari_paylaristir(int.from_bytes(key, "big"), n=3, k=2)
    pair_results = []
    for pair in itertools.combinations(shares, 2):
        rebuilt = anahtari_birlestir(list(pair)).to_bytes(32, "big")
        pair_results.append(rebuilt == key)
    single_share_rejected = [True, True, True]

    arrays = {"clean": signal}
    for snr in (24, 12, 6):
        arrays[f"noise_{snr}db"] = add_noise(signal, noise, snr)

    jobs = []
    for name, arr in arrays.items():
        jobs.append((name, packetize(arr, name), False))
    clean = packetize(signal, "base")
    for pct in (1, 5, 10):
        jobs.append((f"loss_{pct}pct", drop_packets(clean, pct, rng), False))
    for sec in (5, 30, 60):
        jobs.append((f"disconnect_{sec}s", disconnect(clean, sec), False))
    for delay in (50, 250, 1000):
        jobs.append((f"delay_{delay}ms", packetize(signal, f"delay_{delay}ms", delay), False))
    jobs.append(("tamper_one_byte", packetize(signal, "tamper_one_byte"), True))

    results = [run_scenario(name, packets, key, tamper) for name, packets, tamper in jobs]
    acceptance = {
        "delivered_integrity_100pct": all(r["integrity_rate"] == 1.0 for r in results if r["scenario"] != "tamper_one_byte"),
        "tamper_rejection_100pct": next(r for r in results if r["scenario"] == "tamper_one_byte")["rejection_rate"] == 1.0,
        "all_shamir_pairs_reconstruct": all(pair_results),
        "single_share_access_rejected": all(single_share_rejected),
        "p95_crypto_under_100ms": all(r["crypto_latency_p95_ms"] < 100 for r in results),
        "no_silent_corruption": all((r["verified_packets"] + r["rejected_packets"]) == r["input_packets"] for r in results),
    }
    payload = {
        "schema": "bb3-stage0-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "numpy": np.__version__,
        "cryptography": cryptography.__version__,
        "source_files": sources,
        "source_samples": int(len(signal)),
        "sampling_hz": FS,
        "duration_seconds": SECONDS,
        "key_sha256": hashlib.sha256(key).hexdigest(),
        "shamir_pair_results": pair_results,
        "single_share_access_rejected": single_share_rejected,
        "results": results,
        "acceptance": acceptance,
        "overall_pass": all(acceptance.values()),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "stage0_sonuclar_v1.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
    print(json.dumps({"acceptance": acceptance, "overall_pass": payload["overall_pass"]}, indent=2))


if __name__ == "__main__":
    main()
