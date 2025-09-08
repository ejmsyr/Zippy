##Keys
tot = 91
pub = 5
pri = 29

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

def decode(encoded_str, dictionary):
    decoded_indices = []
    # Each encoded number is 2 digits
    for i in range(0, len(encoded_str), 2):
        y_str = encoded_str[i:i+2]
        if len(y_str) == 2:
            y = int(y_str)
            # x = pow(y, pri, tot)
            x = pow(y, pri, tot)
            decoded_indices.append(f"{x:02}")
    # Now map indices back to chars
    output = []
    for idx in decoded_indices:
        if idx in dictionary:
            output.append(dictionary[idx])
        else:
            output.append('?')  # Unknown index
    return ''.join(output)

if __name__ == "__main__":
    with open("encoded.txt", "r") as f:
        lines = f.readlines()
    dict_str = lines[0].strip()
    encoded_str = lines[1].strip()
    dictionary = parse_dictionary(dict_str)
    decoded = decode(encoded_str, dictionary)
    print(decoded)