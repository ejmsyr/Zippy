import json
import os
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return result.returncode, result.stdout


def test_roundtrip(tmp_path: Path):
    # Prepare input
    sample_text = "The quick brown fox jumps over the lazy dog.\n"
    in_file = tmp_path / "sample.txt"
    out_json = tmp_path / "out.json"
    in_file.write_text(sample_text)

    # Encode
    code, out = run([sys.executable, "Zipper.py", "--input", str(in_file), "--output", str(out_json), "--rounds", "2", "--chunk-size", "2", "--salt-length", "8"])
    assert code == 0, f"Encoder failed: {out}"
    assert out_json.exists(), "Output JSON not created"

    # Basic JSON sanity
    data = json.loads(out_json.read_text())
    assert isinstance(data, list) and len(data) >= 1
    assert "encoded_indices" in data[0]

    # Decode (stdout)
    code, decoded = run([sys.executable, "Unzippy.py", "--input", str(out_json)])
    assert code == 0, f"Decoder failed: {decoded}"
    assert decoded == sample_text, f"Roundtrip mismatch: {decoded!r} vs {sample_text!r}"
