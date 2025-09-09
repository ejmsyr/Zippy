# Zippy: Plan for Maximum Security Implementation

## 1. Key Management

- **Use large prime numbers for modulus (`tot`) and keys (`pub`, `pri`)**  
  - Generate keys using a secure random number generator.
  - Store keys securely, separate from encoded files.
  - Optionally, allow user-supplied passphrases to derive keys.

## 2. Dictionary Obfuscation

- **Randomize dictionary order**  
  - Use a cryptographically secure shuffle based on a key or nonce.
- **Encrypt the dictionary**  
  - Use symmetric encryption (e.g., AES) to encrypt the dictionary before saving.
  - Store the IV (initialization vector) with the encoded file.

## 3. Encoding Process

- **Chunk-based encoding**  
  - Allow variable chunk sizes (configurable, e.g., 2–4 bytes).
  - Pad input to ensure all chunks are the same size.
- **Multiple encoding rounds**  
  - After initial encoding, re-encode the output with a new dictionary and key.
  - Store metadata for each round (e.g., chunk size, IV, key ID).

## 4. Output Obfuscation

- **Add salt/nonce to each encoding session**  
  - Store salt/nonce with the encoded file.
- **Obfuscate output further**  
  - Optionally, compress the encoded output using a standard algorithm (e.g., zlib).
  - Optionally, base64-encode the final output for safe transport.

## 5. Decoding Process

- **Require all keys, salts, IVs, and metadata for decoding**
- **Reverse all encoding rounds in order**
- **Decrypt the dictionary before use**

## 6. File and Data Handling

- **Support for binary files as well as text**
- **Securely erase temporary files after use**
- **Validate input and output for integrity (e.g., checksums or HMAC)**

## 7. User Interface

- **Command-line interface with options for:**
  - Setting chunk size
  - Number of encoding rounds
  - Key management (generate, import, export)
  - Encrypting/decrypting dictionary
  - Compression options

## 8. Documentation & Testing

- **Document all algorithms and options**
- **Provide usage examples**
- **Include unit and integration tests for all features**

---

## Implementation Steps

1. **Key Generation Module**
   - Generate large primes and keys.
   - Save/load keys securely.

2. **Dictionary Module**
   - Build, randomize, and encrypt dictionary.
   - Decrypt and parse dictionary for decoding.

3. **Encoding/Decoding Core**
   - Implement chunk-based, multi-round encoding/decoding.
   - Integrate modular exponentiation and output obfuscation.

4. **File Handling**
   - Support text and binary files.
   - Manage metadata, salts, IVs, and secure deletion.

5. **CLI & User Experience**
   - Build command-line interface with all options.
   - Add help and documentation.

6. **Testing & Validation**
   - Write tests for each module.
   - Validate security and correctness.

---

## Security Notes

- **Never hardcode keys in source code.**
- **Use established cryptographic libraries for encryption and randomization.**
- **Review code for side-channel and implementation vulnerabilities.**

---

**Goal:**  
Make Zippy a robust, flexible, and as-secure-as-possible educational tool for custom encoding and encryption workflows. 