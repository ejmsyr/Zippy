# Zippy

**Zippy** is a simple, educational text compressor and decompressor written in Python.  
It demonstrates dictionary-based encoding, modular exponentiation for obfuscation, and basic file I/O.  
Zippy is not intended for production use, but as a learning tool for custom encoding and decoding workflows.

---

## Features

- **Dictionary Encoding:**  
  Each unique character in the input is assigned a 2-digit index as it appears.
- **Modular Exponentiation:**  
  Each index is obfuscated using modular exponentiation (`y = x^pub mod tot`) for basic encryption.
- **File Output:**
  The encoded data for each round is saved to `encoded_output.txt`, while private keys are stored separately in `private_keys.json`.
- **Decoding:**
  The `Unzippy.py` script reverses the process using private keys stored separately in `private_keys.json`.

---

## How It Works

### Compression (`Zipper.py`)

1. **Read Input:**  
   Reads the contents of `texsample.txt`.
2. **Build Dictionary:**  
   Assigns each unique character a 2-digit index in order of appearance.
3. **Encode:**
   Replaces each character with its index, then encodes each 2-digit index using modular exponentiation.
4. **Save:**
   Writes round metadata to `encoded_output.txt` and saves the private keys to `private_keys.json`.

### Decompression (`Unzippy.py`)

1. **Read Encoded File:**
   Loads the dictionary and encoded string from `encoded_output.txt`.
2. **Decode:**
   Uses the private keys supplied by the caller to reverse the modular exponentiation and recover the original indices.
3. **Reconstruct:**  
   Maps indices back to characters using the dictionary and prints the original text.

---

## Usage

### Compress

```bash
python Zipper.py
```

- Input: `texsample.txt`
- Output: `encoded_output.txt` and `private_keys.json`

### Decompress

```bash
python Unzippy.py
```

- Input: `encoded_output.txt` and `private_keys.json`
- Output: Prints the reconstructed original text to the terminal

---

## Example

**Input (`texsample.txt`):**
```
hello world
```

**Output (`encoded_output.txt`):**
```
h00e01l02o03 04w05r06d07
0001020203044053056032037
```

---

## File Structure

```
Zippy/
├── Zipper.py
├── Unzippy.py
├── texsample.txt
├── encoded_output.txt
├── private_keys.json
```

---

## Notes

- The private keys are saved to `private_keys.json` and must be supplied during decoding.
- The encoding is not cryptographically secure.
- For educational and experimental use only.

---

**Author:**  
[Your Name Here]