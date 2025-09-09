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
  The dictionary and encoded data are saved to `encoded.txt`.
- **Decoding:**  
  The `Unzippy.py` script reverses the process using the private key.

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
   Writes the dictionary and encoded string to `encoded.txt`.

### Decompression (`Unzippy.py`)

1. **Read Encoded File:**  
   Loads the dictionary and encoded string from `encoded.txt`.
2. **Decode:**  
   Uses the private key to reverse the modular exponentiation and recover the original indices.
3. **Reconstruct:**  
   Maps indices back to characters using the dictionary and prints the original text.

---

## Usage

### Compress

```bash
python Zipper.py
```

- Input: `texsample.txt`
- Output: `encoded.txt` (dictionary on the first line, encoded string on the second)

### Decompress

```bash
python Unzippy.py
```

- Input: `encoded.txt`
- Output: Prints the reconstructed original text to the terminal

---

## Example

**Input (`texsample.txt`):**
```
hello world
```

**Output (`encoded.txt`):**
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
├── encoded.txt
```

---

## Notes

- Keys are generated with 2048-bit primes by default, producing large RSA moduli.
- The encoding is not cryptographically secure.
- For educational and experimental use only.

---

**Author:**
[Your Name Here]
