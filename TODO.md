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
