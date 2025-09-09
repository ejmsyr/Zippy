import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
import json
import zlib

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
    print(f"encoded_input_str (len {len(encoded_input_str)}, type {type(encoded_input_str)}): {encoded_input_str}")
    if is_obfuscated:
        # Base64 decode
        compressed_encoded_str = base64.urlsafe_b64decode(encoded_input_str.encode('utf-8'))
        print(f"compressed_encoded_str (len {len(compressed_encoded_str)}, type {type(compressed_encoded_str)}): {compressed_encoded_str}")
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

def multi_round_decode():
    with open("encoded_output.txt", "r") as f:
        all_round_data = json.load(f)

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

        if i == len(all_round_data) - 1: # Last round in the encoding process (first to decode)
            encoded_str_for_this_round = round_data["encoded_indices"]
        else:
            encoded_str_for_this_round = current_decoded_indices_str # Output of previous decode is input for this decode

        current_decoded_indices_str = single_round_decode(encoded_str_for_this_round, tot, pri, chunk_size, original_indices_len, salt_length, is_obfuscated)

        if i == 0: # First round in the encoding process (last to decode)
            iv_b64 = round_data["iv"]
            encrypted_dict_b64 = round_data["encrypted_dict"]

            # Decrypt the dictionary
            key = hashlib.sha256(str(pri).encode()).digest()
            iv = base64.b64decode(iv_b64)
            encrypted_dict = base64.b64decode(encrypted_dict_b64)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_dict_str = unpad(cipher.decrypt(encrypted_dict), AES.block_size).decode()

            dictionary = parse_dictionary(decrypted_dict_str)

            # Now map indices back to chars
            output = []
            for j in range(0, len(current_decoded_indices_str), 2): # Iterate by 2 digits for each character index
                idx = current_decoded_indices_str[j:j+2]
                if idx in dictionary:
                    output.append(dictionary[idx])
                else:
                    output.append('?')  # Unknown index
            return ''.join(output)

if __name__ == "__main__":
    decoded_text = multi_round_decode()
    print(decoded_text)