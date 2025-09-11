"""
Standalone smoke tests for Zippy encoder/decoder.

Runs a matrix of configurations without external dependencies.
Exits non-zero on failure, prints progress and results.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def scenario(name: str, text: str, rounds: int, chunk: int, salt: int, obfuscate: bool):
    with tempfile.TemporaryDirectory() as d:
        dpath = Path(d)
        inp = dpath / "in.txt"
        out_json = dpath / "out.json"
        inp.write_text(text)

        enc_cmd = [sys.executable, "Zipper.py", "-i", str(inp), "-o", str(out_json), "-r", str(rounds), "-c", str(chunk), "-s", str(salt)]
        if obfuscate:
            enc_cmd.append("--obfuscate")
        else:
            enc_cmd.append("--no-obfuscate")

        e = run(enc_cmd)
        if e.returncode != 0:
            print(f"[FAIL] {name}: encoder failed\n{e.stdout}")
            return False
        if not out_json.exists():
            print(f"[FAIL] {name}: out.json not created")
            return False

        try:
            data = json.loads(out_json.read_text())
        except Exception as ex:
            print(f"[FAIL] {name}: invalid JSON: {ex}")
            return False
        if not isinstance(data, list) or not data:
            print(f"[FAIL] {name}: JSON missing rounds")
            return False

        dec_cmd = [sys.executable, "Unzippy.py", str(out_json)]
        dproc = run(dec_cmd)
        if dproc.returncode != 0:
            print(f"[FAIL] {name}: decoder failed\n{dproc.stdout}")
            return False
        out = dproc.stdout
        if out != text:
            print(f"[FAIL] {name}: mismatch\nExpected: {text!r}\nGot     : {out!r}")
            return False

        # Also verify decode from stdin
        dproc2 = subprocess.run([sys.executable, "Unzippy.py", "-i", "-"], input=out_json.read_text(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if dproc2.returncode != 0 or dproc2.stdout != text:
            print(f"[FAIL] {name}: stdin decode mismatch\nExpected: {text!r}\nGot     : {dproc2.stdout!r}")
            return False

        print(f"[OK] {name}")
        return True


def main():
    tests = [
        ("default-2r-obf", "The quick brown fox jumps over the lazy dog.\n", 2, 2, 16, True),
        ("1r-noobf", "Hello, world!\n", 1, 2, 0, False),
        ("3r-obf-chunk3", "Sphinx of black quartz, judge my vow.\n", 3, 3, 8, True),
        ("stdin-2r-obf", "Vita brevis, ars longa.\n", 2, 2, 4, True),
        ("chunk4-2r-obf", "Waltz, bad nymph, for quick jigs vex.\n", 2, 4, 12, True),
        ("2r-noobf-chunk2-salt8", "Pack my box with five dozen liquor jugs.\n", 2, 2, 8, False),
    ]

    ok = True
    for name, text, r, c, s, obf in tests:
        if name.startswith("stdin"):
            # Special handling: feed input via stdin
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                from pathlib import Path
                out_json = Path(d) / "out.json"
                enc_cmd = [sys.executable, "Zipper.py", "-i", "-", "-o", str(out_json), "-r", str(r), "-c", str(c), "-s", str(s)]
                if obf:
                    enc_cmd.append("--obfuscate")
                else:
                    enc_cmd.append("--no-obfuscate")
                e = subprocess.run(enc_cmd, input=text, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                if e.returncode != 0 or not out_json.exists():
                    print(f"[FAIL] {name}: encoder failed\n{e.stdout}")
                    ok = False
                    continue
                dproc = subprocess.run([sys.executable, "Unzippy.py", "-i", str(out_json)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                if dproc.returncode != 0 or dproc.stdout != text:
                    print(f"[FAIL] {name}: mismatch\nExpected: {text!r}\nGot     : {dproc.stdout!r}")
                    ok = False
                    continue
                print(f"[OK] {name}")
        else:
            ok &= scenario(name, text, r, c, s, obf)

    # Binary scenario
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        from pathlib import Path
        dpath = Path(d)
        # Construct arbitrary bytes including nulls and non-ASCII
        bdata = bytes([0, 1, 2, 3, 255, 128, 64, 10, 13, 42, 99, 250])
        inp = dpath / "in.bin"
        out_json = dpath / "out.json"
        out_bin = dpath / "out.bin"
        inp.write_bytes(bdata)
        enc = subprocess.run([sys.executable, "Zipper.py", "-i", str(inp), "-o", str(out_json), "--binary", "-r", "2"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if enc.returncode != 0 or not out_json.exists():
            print("[FAIL] binary: encoder failed\n" + enc.stdout)
            ok = False
        else:
            dec = subprocess.run([sys.executable, "Unzippy.py", "-i", str(out_json), "-o", str(out_bin)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if dec.returncode != 0 or not out_bin.exists():
                print("[FAIL] binary: decoder failed\n" + dec.stdout)
                ok = False
            else:
                if out_bin.read_bytes() != bdata:
                    print("[FAIL] binary: roundtrip mismatch")
                    ok = False
                else:
                    print("[OK] binary")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
