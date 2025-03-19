encrypt_data

Overview

encrypt_data is a Python package that simplifies the process of encrypting and decrypting data using Hybrid Encryption (a combination of asymmetric and symmetric encryption). This package makes it easy to securely transfer sensitive data over networks while maintaining integrity and confidentiality.

Features

Simplified Encryption & Decryption: Encrypt and decrypt data easily with minimal steps.

Hybrid Encryption: Utilizes both asymmetric (RSA) and symmetric (AES) encryption for better security.

Secure Data Transfer: Enables secure transmission of bulk data over networks.

Integrity Check: Uses hashing (SHA-512) to ensure data integrity during transmission.

Easy Integration: Can be seamlessly integrated into any Python application.

Installation

To install the package, use:

pip install encrypt_data

Package Structure

encrypt_data/
|__ encrypt_data/
|    |__ __init__.py
|    |__ main.py
|__ setup.py
|__ README.md

Usage

Encryption

from encrypt_data import Encrypt

public_key = "-----BEGIN RSA PUBLIC KEY----------END RSA PUBLIC KEY-----\n"
encrypt = Encrypt(public_key)
encryption_data = {'payload': {"name": "john"}}
data_encrypted = encrypt.encrypt_data(data_to_be_encrypted=encryption_data)

Decryption

from encrypt_data import Decrypt

private_key = """-----BEGIN RSA PRIVATE KEY----------END RSA PRIVATE KEY-----"""
decrypt = Decrypt(private_key=private_key, data_to_be_decrypted=data_encrypted['encrypted_data'])
data_decrypted = decrypt.decrypt_data()

How It Works

Key Generation: The package uses an RSA public-private key pair for encryption and decryption.

Symmetric Key Encryption: A symmetric key (AES) is generated and encrypted using RSA public key.

Data Encryption: Data is encrypted using the symmetric key.

Data Transmission: The encrypted symmetric key and encrypted data are sent over the network.

Decryption:

The symmetric key is decrypted using the private key.

The data is decrypted using the decrypted symmetric key.

The hash is verified to check data integrity.

Security Measures

Uses RSA for asymmetric encryption and Fernet (AES-based) encryption for symmetric encryption.

Implements SHA-512 hashing to detect tampering.

Encrypts both the symmetric key and the actual data for better security.

Ensures data integrity through hash verification after decryption.

License

This package is released under the MIT License.