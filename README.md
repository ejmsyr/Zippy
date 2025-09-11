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
   Writes per-round metadata and encoded data as JSON to `encoded_output.txt`.

### Decompression (`Unzippy.py`)

1. **Read Encoded File:**  
   Loads per-round metadata and encoded strings from `encoded_output.txt`.
2. **Decode:**  
   Uses the private key to reverse the modular exponentiation and recover the original indices.
3. **Reconstruct:**  
   Maps indices back to characters using the dictionary and prints the original text.

---

## Usage

### CLI

Both encoder and decoder provide a simple CLI with sensible defaults.

Commonly used options:
- `--input/-i`: input file path
- `--output/-o`: output file path (JSON for encoder, text for decoder)
- `--rounds/-r`: number of encoding rounds (encoder)
- `--chunk-size/-c`: chunk size in digits per char index (encoder)
- `--salt-length/-s`: salt digits appended per round (encoder)
- `--obfuscate/--no-obfuscate`: toggle zlib+base64 obfuscation (encoder)

### Compress

```bash
python Zipper.py --input texsample.txt --output encoded_output.txt --rounds 2 --chunk-size 2 --salt-length 16 --obfuscate
```

- Input: `texsample.txt`
- Output: `encoded_output.txt` (JSON array with one object per round)

Minimal: encode literal text
```bash
python Zipper.py 'Hello world!' --output out.json
```

### Decompress

```bash
python Unzippy.py --input encoded_output.txt --output decoded.txt
```

Minimal: decode from stdin
```bash
cat encoded_output.txt | python Unzippy.py -i - > decoded.txt
```

Positional path also works
```bash
python Unzippy.py encoded_output.txt --output decoded.txt
```

- Input: `encoded_output.txt`
- Output: Prints the reconstructed original text to the terminal

---

## Example

Run `python Zipper.py` to produce `encoded_output.txt`, then `python Unzippy.py` to print the original text.

---

## File Structure

```
Zippy/
├── Zipper.py
├── Unzippy.py
├── texsample.txt
├── encoded_output.txt
```

---

## Notes

- The keys (`tot`, `pub`, `pri`) are generated per round for demonstration and stored in `encoded_output.txt` for decoding.
- The encoding is not cryptographically secure.
- For educational and experimental use only.

Optional dependency: If PyCryptodome is unavailable, the encoder stores a base64 plaintext dictionary for decoding instead of AES-encrypting it.

---

**Author:**  
[Your Name Here]
<<<<<<< Updated upstream
## Testing

To run the unit tests:

```bash
pip install -r requirements.txt
pytest
```
=======
>>>>>>> Stashed changes
