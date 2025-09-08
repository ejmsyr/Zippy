##Keys
tot=91
pub=5
pri=29
# 
def simple_encode(text):
    dictionary = {}
    output_dict = []
    output_indices = []
    idx = 0

    for char in text:
        if char not in dictionary:
            dictionary[char] = f"{idx:02}"
            output_dict.append(f"{char}{dictionary[char]}")
            output_indices.append(dictionary[char])
            idx += 1
        else:
            output_indices.append(dictionary[char])

    dict_str = ''.join(output_dict)

    # Compute step: encode each 2-digit number using y = x^pub mod tot
    indices_str = ''.join(output_indices)
    encoded_nums = []
    for i in range(0, len(indices_str), 2):
        num_str = indices_str[i:i+2]
        if len(num_str) == 2:
            x = int(num_str)
            y = pow(x, pub, tot)
            encoded_nums.append(f"{y:02}")
    encoded_str = ''.join(encoded_nums)

    # Write only the dictionary and encoded portions to file
    with open("encoded.txt", "w") as f:
        f.write(f"{dict_str}\n")
        f.write(f"{encoded_str}\n")

if __name__ == "__main__":
    with open("texsample.txt", "r") as f:
        input_text = f.read()
    simple_encode(input_text)


