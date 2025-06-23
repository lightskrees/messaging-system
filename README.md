This chat system is built with the FastAPI async web framework with E2E encryption in real-time communication using WebSockets over a single TSL connection. 
it is not meant for production but we leveraged some methodologies that enhance data integrity and avoid MITM attacks, tampering data,.... over an insecure network such as:

- JWT authentication mechanism;
- Public/Private key pairs for secure message exchange;
- Keys are managed through a Diffie-Hellman key exchange system where:
  - Private keys are stored locally in a secure directory;
  - Public keys are stored in the central database.

- client-server handshake with ECDH asymetric encryption;
- session key derivation for AES-GCM encryption/decryption for communication over the network;
- database encryption for local database SQLite with SQLCipher ;
