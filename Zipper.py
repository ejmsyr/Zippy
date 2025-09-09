import random
import hashlib
import json
import zlib
from KeyGenerator import generate_keys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64

def single_round_rsa_encode(input_data, tot, pub, chunk_size=2, is_first_round=True, pri_key_for_shuffle=None):
    dict_str = ""
    iv = b""
    encrypted_dict = b""
    original_indices_str = ""

    if is_first_round:
        # Create a seeded random number generator for deterministic shuffle
        seed = int(hashlib.sha256(str(pri_key_for_shuffle).encode()).hexdigest(), 16)
        seeded_random = random.Random(seed)

        unique_chars = sorted(list(set(input_data)))
        seeded_random.shuffle(unique_chars)

        dictionary = {char: f"{i:02}" for i, char in enumerate(unique_chars)}

        dict_str = "".join([f"{char}{dictionary[char]}" for char in unique_chars])

        output_indices = [dictionary[char] for char in input_data]
        original_indices_str = ''.join(output_indices)

        # Encrypt the dictionary
        key = hashlib.sha256(str(pri_key_for_shuffle).encode()).digest()
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_dict = cipher.encrypt(pad(dict_str.encode(), AES.block_size))
    else:
        original_indices_str = input_data # Input is already indices_str

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
        "encoded_indices_raw": encoded_str_raw,
        "original_indices_len": len(original_indices_str),
        "tot": tot,
        "pub": pub,
        "chunk_size": chunk_size
    }

def multi_round_encode(text, num_rounds, initial_chunk_size=2, salt_length=0, obfuscate_output=True):
    all_round_data = []
    current_input_for_next_round = text # This will be the raw data for the next round

    for i in range(num_rounds):
        tot, pub, pri = generate_keys() # New keys for each round
        
        # Encode the current input using RSA
        round_rsa_data = single_round_rsa_encode(current_input_for_next_round, tot, pub, initial_chunk_size, is_first_round=(i == 0), pri_key_for_shuffle=pri)
        
        encoded_str_raw = round_rsa_data["encoded_indices_raw"]

        # Add salt/nonce
        if salt_length > 0:
            salt = ''.join(random.choices('0123456789', k=salt_length)) # Random digits as salt
            encoded_str_with_salt = encoded_str_raw + salt
        else:
            encoded_str_with_salt = encoded_str_raw

        # Compress and base64 encode the encoded_str_with_salt
        if obfuscate_output:
            compressed_encoded_str = zlib.compress(encoded_str_with_salt.encode())
            final_encoded_bytes = base64.urlsafe_b64encode(compressed_encoded_str)
            final_encoded_str = final_encoded_bytes.decode('utf-8')
        else:
            final_encoded_str = encoded_str_raw # Store raw if not obfuscating

        # Store all data for the round
        round_data = {
            "iv": round_rsa_data["iv"],
            "encrypted_dict": round_rsa_data["encrypted_dict"],
            "encoded_indices": final_encoded_str,
            "original_indices_len": round_rsa_data["original_indices_len"],
            "tot": tot,
            "pub": pub,
            "pri": pri, # Store pri for decoding
            "chunk_size": initial_chunk_size,
            "salt_length": salt_length,
            "is_obfuscated": obfuscate_output
        }
        all_round_data.append(round_data)

        # Prepare input for the next round: it's the raw encoded indices from this round
        current_input_for_next_round = encoded_str_raw

    # Store all round data in a single file
    with open("encoded_output.txt", "w") as f:
        f.write(json.dumps(all_round_data, indent=4))

if __name__ == "__main__":
    with open("texsample.txt", "r") as f:
        input_text = f.read()
    
    num_rounds = 2 # Example number of rounds
    initial_chunk_size = 2
    salt_length = 16 # Example salt length
    obfuscate_output = True # Example obfuscation setting
    multi_round_encode(input_text, num_rounds, initial_chunk_size, salt_length, obfuscate_output)

    # Remove keys.txt as keys are now stored per round in multi_encoded.json
    # import os
    # if os.path.exists("keys.txt"):
    #     os.remove("keys.txt")
