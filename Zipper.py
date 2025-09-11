import hashlib
import json
import zlib
<<<<<<< Updated upstream
import base64
import math
import secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.Random import random as crypto_random
from KeyGenerator import generate_keys


def _secure_deterministic_prng(seed: bytes) -> crypto_random.StrongRandom:
    """Create a cryptographically secure deterministic PRNG.

    The generator is seeded with ``seed`` and produces reproducible output by
    deriving random bytes from SHA-256 in counter mode.  The resulting PRNG
    exposes the same interface as ``random.Random`` but uses strong randomness
    internally.
    """

    seed_hash = hashlib.sha256(seed).digest()
    counter = 0

    def randfunc(n: int) -> bytes:
        nonlocal counter
        output = b""
        while len(output) < n:
            ctr_bytes = counter.to_bytes(16, "big")
            output += hashlib.sha256(seed_hash + ctr_bytes).digest()
            counter += 1
        return output[:n]

    return crypto_random.StrongRandom(randfunc=randfunc)
=======
from KeyGenerator import generate_keys
import base64
import argparse
import sys
from pathlib import Path

# Optional dependency: PyCryptodome. Provide graceful fallback when unavailable.
try:
    from Crypto.Cipher import AES  # type: ignore
    from Crypto.Util.Padding import pad  # type: ignore
    from Crypto.Random import get_random_bytes  # type: ignore
    HAVE_CRYPTO = True
except Exception:
    import os
    HAVE_CRYPTO = False

    def pad(data: bytes, block_size: int) -> bytes:  # PKCS#7-like padding
        pad_len = (block_size - (len(data) % block_size)) or block_size
        return data + bytes([pad_len]) * pad_len

    def get_random_bytes(n: int) -> bytes:
        return os.urandom(n)
>>>>>>> Stashed changes

def single_round_rsa_encode(input_data, tot, pub, chunk_size=2, is_first_round=True, pri_key_for_shuffle=None):
    dict_str = ""
    iv = b""
    encrypted_dict = b""
    original_indices_str = ""

    if is_first_round:
        # Create a seeded cryptographically secure PRNG for deterministic shuffle
        seed_bytes = str(pri_key_for_shuffle).encode()
        seeded_random = _secure_deterministic_prng(seed_bytes)

        unique_chars = sorted(list(set(input_data)))
        seeded_random.shuffle(unique_chars)

        dictionary = {char: f"{i:02}" for i, char in enumerate(unique_chars)}

        dict_str = "".join([f"{char}{dictionary[char]}" for char in unique_chars])

        output_indices = [dictionary[char] for char in input_data]
        original_indices_str = ''.join(output_indices)

        # Encrypt the dictionary when Crypto is available; otherwise store plaintext (base64)
        if HAVE_CRYPTO:
            key = hashlib.sha256(str(pri_key_for_shuffle).encode()).digest()
            iv = get_random_bytes(AES.block_size)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted_dict = cipher.encrypt(pad(dict_str.encode(), AES.block_size))
            dict_b64 = ""
        else:
            dict_b64 = base64.b64encode(dict_str.encode()).decode()
    else:
        original_indices_str = input_data # Input is already indices_str
        dict_b64 = ""

    indices_str_to_encode = original_indices_str

    # Pad indices_str
    padding_needed = (chunk_size * 2) - (len(indices_str_to_encode) % (chunk_size * 2))
    if padding_needed != (chunk_size * 2): # Only pad if not already a multiple
        indices_str_to_encode += '0' * padding_needed # Pad with '0's

    encoded_nums = []
    block_size = len(str(tot))
    for i in range(0, len(indices_str_to_encode), chunk_size * 2):
        num_str = indices_str_to_encode[i:i + (chunk_size * 2)]
        x = int(num_str)
        y = pow(x, pub, tot)
        encoded_nums.append(f"{y:0{block_size}}")
    encoded_str_raw = ''.join(encoded_nums)

    return {
        "iv": base64.b64encode(iv).decode() if iv else "",
        "encrypted_dict": base64.b64encode(encrypted_dict).decode() if encrypted_dict else "",
        "dict_b64": dict_b64,
        "encoded_indices_raw": encoded_str_raw,
        "original_indices_len": len(original_indices_str),
        "tot": tot,
        "pub": pub,
        "chunk_size": chunk_size
    }

def multi_round_encode(text, num_rounds, initial_chunk_size=2, salt_length=0, obfuscate_output=True, output_path: str = "encoded_output.txt", is_binary: bool = False):
    all_round_data = []
    current_input_for_next_round = text # This will be the raw data for the next round

    for i in range(num_rounds):
        tot, pub, pri = generate_keys() # New keys for each round
        
        # Encode the current input using RSA
        round_rsa_data = single_round_rsa_encode(current_input_for_next_round, tot, pub, initial_chunk_size, is_first_round=(i == 0), pri_key_for_shuffle=pri)
        
        encoded_str_raw = round_rsa_data["encoded_indices_raw"]

        # Add salt/nonce
        if salt_length > 0:
            entropy = salt_length * math.log2(10)
            if entropy < 32:
                raise ValueError("Salt length must provide at least 32 bits of entropy")
            salt = ''.join(secrets.choice('0123456789') for _ in range(salt_length))
            encoded_str_with_salt = encoded_str_raw + salt
        else:
            encoded_str_with_salt = encoded_str_raw

        # Compress and base64 encode the encoded_str_with_salt
        if obfuscate_output:
            compressed_encoded_str = zlib.compress(encoded_str_with_salt.encode())
            final_encoded_bytes = base64.urlsafe_b64encode(compressed_encoded_str)
            final_encoded_str = final_encoded_bytes.decode('utf-8')
        else:
            # Preserve salt even without obfuscation to keep decode contract consistent
            final_encoded_str = encoded_str_with_salt

        # Store all data for the round
        round_data = {
            "iv": round_rsa_data["iv"],
            "encrypted_dict": round_rsa_data["encrypted_dict"],
            "dict_b64": round_rsa_data.get("dict_b64", ""),
            "encoded_indices": final_encoded_str,
            "original_indices_len": round_rsa_data["original_indices_len"],
            "tot": tot,
            "pub": pub,
            "pri": pri, # Store pri for decoding
            "chunk_size": initial_chunk_size,
            "salt_length": salt_length,
            "is_obfuscated": obfuscate_output
        }
        if i == 0:
            round_data["is_binary"] = bool(is_binary)
        all_round_data.append(round_data)

        # Prepare input for the next round: it's the raw encoded indices from this round
        current_input_for_next_round = encoded_str_raw

    # Store all round data in a single file
    with open(output_path, "w") as f:
        f.write(json.dumps(all_round_data, indent=4))

def _parse_args():
    class _Fmt(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
        pass

    p = argparse.ArgumentParser(
        description=(
            "Zippy encoder: builds a randomized dictionary, encodes chars to indices,\n"
            "applies RSA per chunk, then optionally obfuscates with zlib+base64.\n"
            "Metadata for each round is written to a JSON file."
        ),
        formatter_class=_Fmt,
        epilog=(
            "Examples:\n"
            "  # Encode a sample file with 2 rounds (default)\n"
            "  python Zipper.py -i texsample.txt -o encoded_output.txt\n\n"
            "  # 3 rounds, chunk size 3, 8-digit salt\n"
            "  python Zipper.py -i in.txt -o out.json -r 3 -c 3 -s 8\n\n"
            "  # Minimal: encode literal text\n"
            "  python Zipper.py 'Hello world!' -o out.json\n\n"
            "  # Read input from stdin and disable obfuscation\n"
            "  cat in.txt | python Zipper.py -i - -o out.json --no-obfuscate\n\n"
            "  # Binary mode: encode any bytes (uses Latin-1 mapping)\n"
            "  python Zipper.py -i image.bin -o out.json --binary\n"
        ),
    )
    p.add_argument("text", nargs="?", help="Literal text to encode (overrides --input)")
    p.add_argument("--input", "-i", type=str, default="texsample.txt", help="Path to input text file or '-' for stdin")
    p.add_argument("--output", "-o", type=str, default="encoded_output.txt", help="Path to output JSON file")
    p.add_argument("--rounds", "-r", type=int, default=2, help="Number of encoding rounds (>= 1)")
    p.add_argument("--chunk-size", "-c", type=int, default=2, help="Chunk size in digits per char index (2–4 recommended)")
    p.add_argument("--salt-length", "-s", type=int, default=16, help="Salt length (digits) appended per round (>= 0)")
    p.add_argument("--binary", action="store_true", help="Treat input as binary; map bytes 1:1 via Latin-1")
    obf = p.add_mutually_exclusive_group()
    obf.add_argument("--obfuscate", dest="obfuscate", action="store_true", help="Enable zlib+base64 obfuscation (default)")
    obf.add_argument("--no-obfuscate", dest="obfuscate", action="store_false", help="Disable obfuscation (store raw digits)")
    p.set_defaults(obfuscate=True)
    return p.parse_args()


def main():
    args = _parse_args()
    if args.rounds < 1:
        raise SystemExit("--rounds must be >= 1")
    if args.chunk_size < 1:
        raise SystemExit("--chunk-size must be >= 1")
    if args.salt_length < 0:
        raise SystemExit("--salt-length must be >= 0")

    # Determine source text in order of precedence: positional text -> --text -> --input
    if getattr(args, "text", None):
        text = args.text
    elif args.input == "-":
        text = sys.stdin.buffer.read().decode("latin-1") if args.binary else sys.stdin.read()
    else:
        in_path = Path(args.input)
        text = in_path.read_bytes().decode("latin-1") if args.binary else in_path.read_text()
    multi_round_encode(
        text,
        num_rounds=args.rounds,
        initial_chunk_size=args.chunk_size,
        salt_length=args.salt_length,
        obfuscate_output=args.obfuscate,
        output_path=args.output,
        is_binary=args.binary,
    )


if __name__ == "__main__":
    main()
