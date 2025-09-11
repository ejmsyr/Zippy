import base64
import hashlib
import json
import zlib
import argparse
from pathlib import Path
import sys

# Optional dependency: PyCryptodome. Provide graceful fallback when unavailable.
try:
    from Crypto.Cipher import AES  # type: ignore
    from Crypto.Util.Padding import unpad  # type: ignore
    HAVE_CRYPTO = True
except Exception:
    HAVE_CRYPTO = False

    def unpad(data: bytes, block_size: int) -> bytes:  # PKCS#7-like
        pad_len = data[-1]
        return data[:-pad_len]

def parse_dictionary(dict_str):
    # Example: i00 01a02m03l04...
    dictionary = {}
    i = 0
    while i < len(dict_str):
        char = dict_str[i]
        idx = dict_str[i+1:i+3]
        dictionary[idx] = char
        i += 3
    return dictionary

def single_round_decode(encoded_input_str, tot, pri, chunk_size, original_indices_len, salt_length, is_obfuscated):
    if is_obfuscated:
        # Base64 decode
        compressed_encoded_str = base64.urlsafe_b64decode(encoded_input_str.encode('utf-8'))
        # Decompress
        encoded_str_with_salt = zlib.decompress(compressed_encoded_str).decode()
    else:
        encoded_str_with_salt = encoded_input_str # Input is already raw

    if salt_length > 0:
        encoded_str = encoded_str_with_salt[:-salt_length] # Remove salt
    else:
        encoded_str = encoded_str_with_salt

    decoded_indices = []
    block_size = len(str(tot))
    # Each encoded number is of block_size
    for i in range(0, len(encoded_str), block_size):
        y_str = encoded_str[i:i+block_size]
        if len(y_str) == block_size:
            y = int(y_str)
            x = pow(y, pri, tot)
            decoded_indices.append(f"{x:0{chunk_size * 2}}") # Format with chunk_size * 2 digits

    decoded_indices_str = ''.join(decoded_indices)
    decoded_indices_str = decoded_indices_str[:original_indices_len] # Remove padding
    return decoded_indices_str

def multi_round_decode(input_path: str = "encoded_output.txt"):
    if input_path == "-":
        raw = sys.stdin.read()
        all_round_data = json.loads(raw)
    else:
        with open(input_path, "r") as f:
            all_round_data = json.load(f)
    is_binary = bool(all_round_data[0].get("is_binary", False)) if all_round_data else False

    current_decoded_indices_str = ""

    # Iterate through rounds in reverse order
    for i in range(len(all_round_data) - 1, -1, -1):
        round_data = all_round_data[i]
        
        tot = round_data["tot"]
        pri = round_data["pri"]
        chunk_size = round_data["chunk_size"]
        original_indices_len = round_data["original_indices_len"]
        salt_length = round_data["salt_length"]
        is_obfuscated = round_data["is_obfuscated"]

        if i == len(all_round_data) - 1:  # Last encoded round (first to decode)
            encoded_str_for_this_round = round_data["encoded_indices"]
            use_obfuscation = is_obfuscated
            use_salt_len = salt_length
        else:
            # Earlier rounds receive raw decoded digits from the next round
            encoded_str_for_this_round = current_decoded_indices_str
            use_obfuscation = False
            use_salt_len = 0

        current_decoded_indices_str = single_round_decode(
            encoded_str_for_this_round, tot, pri, chunk_size, original_indices_len, use_salt_len, use_obfuscation
        )

        if i == 0: # First round in the encoding process (last to decode)
            iv_b64 = round_data.get("iv", "")
            encrypted_dict_b64 = round_data.get("encrypted_dict", "")
            dict_b64 = round_data.get("dict_b64", "")

            if encrypted_dict_b64 and iv_b64 and HAVE_CRYPTO:
                # Decrypt the dictionary (Crypto available)
                key = hashlib.sha256(str(pri).encode()).digest()
                iv = base64.b64decode(iv_b64)
                encrypted_dict = base64.b64decode(encrypted_dict_b64)
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted_dict_str = unpad(cipher.decrypt(encrypted_dict), AES.block_size).decode()
            elif dict_b64:
                # Fallback: plaintext dictionary was stored
                decrypted_dict_str = base64.b64decode(dict_b64.encode()).decode()
            else:
                raise RuntimeError("Dictionary decryption unavailable: missing Crypto and no plaintext dictionary present.")

            dictionary = parse_dictionary(decrypted_dict_str)

            # Now map indices back to chars
            output = []
            for j in range(0, len(current_decoded_indices_str), 2): # Iterate by 2 digits for each character index
                idx = current_decoded_indices_str[j:j+2]
                if idx in dictionary:
                    output.append(dictionary[idx])
                else:
                    output.append('?')  # Unknown index
            return ''.join(output), is_binary

def _parse_args():
    class _Fmt(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
        pass

    p = argparse.ArgumentParser(
        description=(
            "Zippy decoder: reverses RSA per chunk for each round (last to first),\n"
            "then reconstructs the plaintext using the first-round dictionary."
        ),
        formatter_class=_Fmt,
        epilog=(
            "Examples:\n"
            "  # Decode a JSON produced by Zipper.py\n"
            "  python Unzippy.py -i encoded_output.txt -o decoded.txt\n\n"
            "  # Print to stdout (default)\n"
            "  python Unzippy.py -i out.json\n"
        ),
    )
    p.add_argument("encoded", nargs="?", help="Path to input JSON (overrides --input) or '-' for stdin")
    p.add_argument("--input", "-i", type=str, default="encoded_output.txt", help="Path to input JSON file")
    p.add_argument("--output", "-o", type=str, default="", help="Optional path to write decoded text; prints to stdout if empty")
    return p.parse_args()


def main():
    args = _parse_args()
    in_arg = args.encoded if getattr(args, "encoded", None) else args.input
    text, is_binary = multi_round_decode(in_arg)
    if args.output:
        if is_binary:
            Path(args.output).write_bytes(text.encode("latin-1"))
        else:
            Path(args.output).write_text(text)
    else:
        import sys as _sys
        if is_binary:
            _sys.stdout.buffer.write(text.encode("latin-1"))
        else:
            _sys.stdout.write(text)


if __name__ == "__main__":
    main()
