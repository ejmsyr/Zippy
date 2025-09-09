import base64
import hashlib
import json

import pytest
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from KeyGenerator import generate_keys
from Zipper import single_round_rsa_encode, multi_round_encode
from Unzippy import (
    parse_dictionary,
    single_round_decode,
    multi_round_decode,
)


def decode_first_round(encoded_data, tot, pri):
    """Helper to decode output of single_round_rsa_encode."""
    decoded_indices = single_round_decode(
        encoded_data["encoded_indices_raw"],
        tot,
        pri,
        encoded_data["chunk_size"],
        encoded_data["original_indices_len"],
        salt_length=0,
        is_obfuscated=False,
    )
    key = hashlib.sha256(str(pri).encode()).digest()
    iv = base64.b64decode(encoded_data["iv"])
    encrypted_dict = base64.b64decode(encoded_data["encrypted_dict"])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    dict_str = unpad(cipher.decrypt(encrypted_dict), AES.block_size).decode()
    dictionary = parse_dictionary(dict_str)
    return "".join(
        dictionary[decoded_indices[i : i + 2]]
        for i in range(0, len(decoded_indices), 2)
    )


def manual_multi_round_decode(all_round_data):
    current = ""
    for i in range(len(all_round_data) - 1, -1, -1):
        round_data = all_round_data[i]
        if current:
            encoded_input = current
            is_obfuscated = False
        else:
            encoded_input = round_data["encoded_indices"]
            is_obfuscated = round_data["is_obfuscated"]
        current = single_round_decode(
            encoded_input,
            round_data["tot"],
            round_data["pri"],
            round_data["chunk_size"],
            round_data["original_indices_len"],
            round_data["salt_length"],
            is_obfuscated,
        )
    first_round = all_round_data[0]
    key = hashlib.sha256(str(first_round["pri"]).encode()).digest()
    iv = base64.b64decode(first_round["iv"])
    encrypted_dict = base64.b64decode(first_round["encrypted_dict"])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    dict_str = unpad(cipher.decrypt(encrypted_dict), AES.block_size).decode()
    dictionary = parse_dictionary(dict_str)
    return "".join(
        dictionary[current[i : i + 2]] for i in range(0, len(current), 2)
    )


def test_single_round_round_trip():
    text = "hello"
    tot, pub, pri = generate_keys()
    encoded = single_round_rsa_encode(text, tot, pub, is_first_round=True, pri_key_for_shuffle=pri)
    decoded = decode_first_round(encoded, tot, pri)
    assert decoded == text


@pytest.mark.parametrize("obfuscate", [True, False])
def test_multi_round_processing(tmp_path, monkeypatch, obfuscate):
    monkeypatch.chdir(tmp_path)
    text = "hello world"
    multi_round_encode(
        text,
        num_rounds=2,
        initial_chunk_size=2,
        salt_length=0,
        obfuscate_output=obfuscate,
    )
    with open("encoded_output.txt") as f:
        data = json.load(f)
    decoded = manual_multi_round_decode(data)
    assert decoded == text


def test_single_round_encode_invalid_input():
    tot, pub, pri = generate_keys()
    with pytest.raises(TypeError):
        single_round_rsa_encode(None, tot, pub, pri_key_for_shuffle=pri)


def test_multi_round_decode_corrupted_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    text = "corrupt me"
    multi_round_encode(text, num_rounds=1, initial_chunk_size=2, salt_length=0, obfuscate_output=True)
    # Corrupt the stored encoded data
    with open("encoded_output.txt") as f:
        data = json.load(f)
    data[0]["encoded_indices"] = data[0]["encoded_indices"][:-1] + "!"
    with open("encoded_output.txt", "w") as f:
        json.dump(data, f)
    with pytest.raises(Exception):
        multi_round_decode()
