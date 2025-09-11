# Zippy TODO List

## Key Management
- [x] Use large prime numbers for modulus (`tot`) and keys (`pub`, `pri`)
- [x] Generate keys using a secure random number generator.
- [ ] Store keys securely, separate from encoded files.
- [ ] Optionally, allow user-supplied passphrases to derive keys.

## Dictionary Obfuscation
- [x] Randomize dictionary order
- [x] Use a cryptographically secure shuffle based on a key or nonce.
- [x] Encrypt the dictionary
- [x] Use symmetric encryption (e.g., AES) to encrypt the dictionary before saving.
- [x] Store the IV (initialization vector) with the encoded file.

## Encoding Process
- [x] Chunk-based encoding
- [x] Allow variable chunk sizes (configurable, e.g., 2–4 bytes).
- [x] Pad input to ensure all chunks are the same size.
- [x] Multiple encoding rounds
- [x] After initial encoding, re-encode the output with a new dictionary and key.
- [x] Store metadata for each round (e.g., chunk size, IV, key ID).

## Output Obfuscation
- [x] Add salt/nonce to each encoding session
- [x] Store salt/nonce with the encoded file.
- [ ] Obfuscate output further
- [ ] Optionally, compress the encoded output using a standard algorithm (e.g., zlib).
- [ ] Optionally, base64-encode the final output for safe transport.

## Decoding Process
- [ ] Require all keys, salts, IVs, and metadata for decoding
- [ ] Reverse all encoding rounds in order
- [ ] Decrypt the dictionary before use

## File and Data Handling
- [ ] Support for binary files as well as text
- [ ] Securely erase temporary files after use
- [ ] Validate input and output for integrity (e.g., checksums or HMAC)

## User Interface
- [ ] Command-line interface with options for:
    - [ ] Setting chunk size
    - [ ] Number of encoding rounds
    - [ ] Key management (generate, import, export)
    - [ ] Encrypting/decrypting dictionary
    - [ ] Compression options

## Documentation & Testing
- [ ] Document all algorithms and options
- [ ] Provide usage examples
- [ ] Include unit and integration tests for all features

## Implementation Steps

### 1. Key Generation Module
- [x] Generate large primes and keys.
- [ ] Save/load keys securely.

### 2. Dictionary Module
- [x] Build and randomize dictionary.
- [x] Encrypt dictionary.
- [x] Decrypt and parse dictionary for decoding.

### 3. Encoding/Decoding Core
- [x] Implement chunk-based encoding/decoding.
- [x] Implement multi-round encoding/decoding.
- [ ] Integrate modular exponentiation and output obfuscation.

### 4. File Handling
- [ ] Support text and binary files.
- [ ] Manage metadata, salts, IVs, and secure deletion.

### 5. CLI & User Experience
- [ ] Build command-line interface with all options.
- [ ] Add help and documentation.

### 6. Testing & Validation
- [ ] Write tests for each module.
- [ ] Validate security and correctness.

---

# Planned Features (Detailed)

The following features are planned with full specifications, CLI design, defaults, and validation strategy.

## 1) Passphrase Key Management
- Goal: Separate key storage from encoded JSON and protect private keys with a passphrase.
- Storage: `keys.json` (separate from `encoded_output.txt`).
- KDF: default `argon2id`; fallback `scrypt` when argon2 is unavailable.
- Wrapping: AES-GCM to encrypt per-round `pri` (includes `nonce` and `tag`).
- Backcompat: If `pri` exists in the encoded JSON, decoder will still accept it.
- CLI (defaults in parentheses):
  - Encoder (Zipper.py):
    - `--passphrase ""` (empty string means disabled)
    - `--key-file keys.json`
    - `--kdf argon2id` (choices: `argon2id`, `scrypt`)
    - `--kdf-time-ms 200`, `--kdf-memory-mb 64`, `--kdf-parallelism 1`
  - Decoder (Unzippy.py):
    - `--passphrase ""` (empty: disabled, expect inline `pri`)
    - `--key-file keys.json`
- JSON changes:
  - encoded_output.txt: remove `pri`, add `key_id` (string) and `schema_version`.
  - keys.json: `{ version, kdf, kdf_params, salt, wrapped_keys: [{key_id, nonce, tag, ciphertext}] }`.
- Tests:
  - Round-trip with passphrase and key file; wrong passphrase fails cleanly.
  - Backwards compatibility with existing files (inline `pri`).

## 2) Integrity & Authenticity
- Goal: Detect tampering and ensure authenticity of data and dictionary.
- HMAC: global HMAC over a canonical JSON form (excluding HMAC field itself).
- AEAD: optional AES-GCM for dictionary to provide authenticity.
- CLI (defaults in parentheses):
  - Encoder: `--hmac false`, `--hmac-key-file hmac.key`, `--aead-dict true`
  - Decoder: `--hmac-key-file hmac.key` (optional; when provided, verification is enforced)
- JSON changes:
  - Top-level: `hmac_alg: "hmac-sha256"`, `hmac: ""` (empty when disabled).
  - Per-round (when AEAD): `dict_nonce`, `dict_tag`.
- Tests:
  - Tamper any field → HMAC verification fails.
  - Wrong AEAD tag → decryption failure with clear error.

## 3) Streaming & Large Files
- Goal: Enable large input support without high memory usage.
- Modes:
  - Two-pass custom dictionary: first pass builds dict; second pass streams encoding.
  - Single-pass `--byte-dict`: fixed dictionary of 256 byte values (00–255).
- CLI (defaults in parentheses):
  - Encoder: `--stream false`, `--byte-dict false`, `--buffer-size 65536`
  - Decoder: `--buffer-size 65536`
- JSON changes:
  - Add `byte_dict: false` and `schema_version`.
- Tests:
  - Generate large file (e.g., 100MB) and stream encode/decode; memory footprint stays bounded.

## 4) Versioned Format, Compression, and Export
- Goal: Make files portable and explicit with versioning and transport options.
- Compression: `--compress {zlib,brotli,none}`; Transport: `--transport {b64,raw}`.
- Minimal export: produce a bundle without sensitive info (`pri`, dict when encrypted), suitable for transport.
- CLI (defaults in parentheses):
  - Encoder: `--format-version 2`, `--compress zlib`, `--transport b64`, `--export-minimal ""` (empty = disabled)
  - Decoder: `--format-version auto` (auto-detect; `auto` by default)
- JSON changes:
  - Top-level: `schema_version`, `compress`, `transport`.
  - Minimal bundle: `{ rounds: [...], schema_version, compress, transport }` without private material.
- Tests:
  - Matrix across compress/transport combos and minimal export round-trip with separate keys.

---

# Current CLI Defaults (for quick start)

Encoder (Zipper.py):
- `--input texsample.txt`
- `--output encoded_output.txt`
- `--rounds 2`
- `--chunk-size 2`
- `--salt-length 16`
- `--obfuscate` (on by default; use `--no-obfuscate` to disable)
- `--binary` (off by default)
- Positional `text` supported (overrides `--input`), or `-i -` to read stdin.

Decoder (Unzippy.py):
- `--input encoded_output.txt`
- `--output ""` (empty prints to stdout)

Minimal usage examples:
- Encode literal: `python Zipper.py 'Hello world' -o out.json`
- Encode from stdin: `cat in.txt | python Zipper.py -i - -o out.json`
- Decode: `python Unzippy.py -i out.json -o out.txt`
