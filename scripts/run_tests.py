"""
Lightweight test runner that does not require pytest.

Runs:
  1) A simple round-trip test (encode -> decode) in-process via subprocess.
  2) The full smoke test matrix (scripts/smoke_tests.py).
Exits non-zero on any failure.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd, **kw):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **kw)


def simple_roundtrip() -> bool:
    sample = "Quick zephyrs blow, vexing daft Jim.\n"
    with tempfile.TemporaryDirectory() as d:
        dpath = Path(d)
        inp = dpath / "in.txt"
        out_json = dpath / "out.json"
        inp.write_text(sample)

        enc = run([sys.executable, "Zipper.py", "-i", str(inp), "-o", str(out_json), "-r", "2", "-c", "2", "-s", "8", "--obfuscate"])
        if enc.returncode != 0:
            print("[FAIL] simple_roundtrip: encoder failed\n" + enc.stdout)
            return False
        if not out_json.exists():
            print("[FAIL] simple_roundtrip: output JSON not created")
            return False

        dec = run([sys.executable, "Unzippy.py", "-i", str(out_json)])
        if dec.returncode != 0:
            print("[FAIL] simple_roundtrip: decoder failed\n" + dec.stdout)
            return False
        if dec.stdout != sample:
            print(f"[FAIL] simple_roundtrip: mismatch\nExpected: {sample!r}\nGot     : {dec.stdout!r}")
            return False
        print("[OK] simple_roundtrip")
        return True


def smoke_suite() -> bool:
    res = run([sys.executable, "scripts/smoke_tests.py"])
    sys.stdout.write(res.stdout)
    return res.returncode == 0


def main():
    ok = simple_roundtrip()
    ok = smoke_suite() and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

