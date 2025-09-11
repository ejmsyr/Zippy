# Zippy

**Zippy** is a simple, educational tool for encoding and decoding text and binary files in Python. It demonstrates several concepts, including dictionary-based encoding, a multi-round RSA-like obfuscation scheme, and the use of salt and obfuscation to make the output more complex. Zippy is not intended for production use but as a learning tool for custom encoding and decoding workflows.

---

## Features

- **Dictionary Encoding:** Each unique character in the input is assigned a 2-digit index.
- **Multi-Round Obfuscation:** The indexed data is obfuscated over multiple rounds using an RSA-like algorithm. New keys are generated for each round.
- **Salting:** A random salt can be added to the encoded data in each round to increase entropy.
- **Obfuscation:** The output of each round can be compressed with `zlib` and encoded with `base64` to make it non-obvious.
- **Binary Mode:** Zippy can handle binary files by mapping each byte to a character using a Latin-1 encoding.
- **Command-Line Interface:** Both the encoder (`Zipper.py`) and decoder (`Unzippy.py`) provide a simple and flexible command-line interface.
- **Optional Cryptography:** Zippy can use `pycryptodome` to encrypt the dictionary, but it will gracefully fall back to a plaintext dictionary if the library is not available.

---

## How It Works

### Encoding (`Zipper.py`)

1.  **Read Input:** Reads the input from a file, stdin, or a command-line argument.
2.  **Build Dictionary:** In the first round, it builds a dictionary that maps each unique character to a 2-digit index.
3.  **Encode:** It then replaces each character with its corresponding index.
4.  **Multi-Round Obfuscation:** For each round, it obfuscates the data using modular exponentiation (`y = x^pub mod tot`).
5.  **Salt and Obfuscate:** It can add a salt to the data and obfuscate it using `zlib` and `base64`.
6.  **Save:** It writes all the data for each round, including the keys and other metadata, to a JSON file.

### Decoding (`Unzippy.py`)

1.  **Read Encoded File:** Loads the per-round metadata and encoded strings from the JSON file.
2.  **Decode:** It processes the rounds in reverse order, using the private key for each round to reverse the modular exponentiation.
3.  **Reconstruct:** In the final step, it uses the dictionary from the first round to map the indices back to characters and reconstruct the original data.

---

## Usage

### Command-Line Interface

Both `Zipper.py` and `Unzippy.py` provide a command-line interface with several options:

**`Zipper.py`**

-   `--input`/`-i`: Path to the input file or `-` for stdin.
-   `--output`/`-o`: Path to the output JSON file.
-   `--rounds`/`-r`: Number of encoding rounds.
-   `--chunk-size`/`-c`: Chunk size in digits per character index.
-   `--salt-length`/`-s`: Number of salt digits to append in each round.
-   `--binary`: Treat the input as a binary file.
-   `--obfuscate`/`--no-obfuscate`: Enable/disable `zlib` and `base64` obfuscation.

**`Unzippy.py`**

-   `--input`/`-i`: Path to the input JSON file or `-` for stdin.
-   `--output`/`-o`: Path to the output file (prints to stdout by default).

### Examples

**Encode a file:**

```bash
python3 Zipper.py -i texsample.txt -o encoded.json
```

**Decode a file:**

```bash
python3 Unzippy.py -i encoded.json -o decoded.txt
```

**Encode a string:**

```bash
python3 Zipper.py "Hello, world!" -o hello.json
```

**Use multiple rounds and a salt:**

```bash
python3 Zipper.py -i texsample.txt -o encoded.json -r 3 -s 16
```

**Encode a binary file:**

```bash
python3 Zipper.py -i my_image.png -o image.json --binary
```

**Decode from stdin:**

```bash
cat encoded.json | python3 Unzippy.py -i -
```

---

## File Structure

```
Zippy/
├── .git/
├── .venv/
├── scripts/
│   ├── run_tests.py
│   └── smoke_tests.py
├── tests/
│   ├── test_cli_roundtrip.py
│   └── test_zippy.py
├── KeyGenerator.py
├── Zipper.py
├── Unzippy.py
├── requirements.txt
├── README.md
├── Makefile
├── TODO.md
└── ...
```

---

## Testing

To run the tests, first install the dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Then, run the test script:

```bash
python3 scripts/run_tests.py
```

---

## Project Status

This project is intended for educational purposes only and is not suitable for production use. The obfuscation scheme is not cryptographically secure.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.