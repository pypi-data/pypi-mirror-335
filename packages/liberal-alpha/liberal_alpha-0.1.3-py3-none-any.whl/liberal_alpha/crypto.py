#!/usr/bin/env python3
"""
crypto.py - Encryption and Decryption functions for Liberal Alpha SDK

This module provides functions for key derivation, ECIES decryption,
AES-GCM decryption (for alpha messages), and utilities for handling Ethereum keys.
"""

import logging
import hashlib
import hmac
import struct
import json
import binascii
from typing import Optional, Tuple

from coincurve import PrivateKey
from Crypto.Cipher import AES
from eth_account import Account
from eth_keys import keys

logger = logging.getLogger(__name__)

def hex_to_bytes(hex_string: str) -> bytes:
    """Convert a hex string to bytes, removing 0x prefix if present."""
    if hex_string.startswith('0x'):
        hex_string = hex_string[2:]
    return bytes.fromhex(hex_string)

def concat_kdf(hash_func, z: bytes, s1: bytes, kd_len: int) -> bytes:
    """
    NIST SP 800-56 Concatenation Key Derivation Function.
    Matches the Go implementation.
    """
    k = bytearray()
    counter = 1
    while len(k) < kd_len:
        counter_bytes = struct.pack('>I', counter)
        h_inst = hash_func()
        h_inst.update(counter_bytes)
        h_inst.update(z)
        if s1:
            h_inst.update(s1)
        k.extend(h_inst.digest())
        counter += 1
    return k[:kd_len]

def derive_keys(shared_secret: bytes, s1: bytes, key_len: int) -> Tuple[bytes, bytes]:
    """
    Derive encryption and MAC keys from the shared secret.
    """
    K = concat_kdf(hashlib.sha512, shared_secret, s1, 2 * key_len)
    ke = K[:key_len]
    km = K[key_len:]
    h_inst = hashlib.sha256()
    h_inst.update(km)
    km = h_inst.digest()
    return ke, km

def decrypt_ecies(private_key_hex: str, encrypted_data_hex: str) -> Optional[bytes]:
    """
    Decrypt data that was encrypted with ECIES in the Go implementation.
    
    Args:
        private_key_hex: Private key as hex string (with or without 0x prefix)
        encrypted_data_hex: Encrypted data as hex string
        
    Returns:
        Decrypted data as bytes or None if decryption fails.
    """
    try:
        # Convert hex strings to bytes
        private_key_bytes = hex_to_bytes(private_key_hex)
        encrypted_bytes = hex_to_bytes(encrypted_data_hex)
        private_key = PrivateKey(private_key_bytes)
        
        # For secp256k1, the ephemeral public key is 65 bytes (uncompressed format)
        pub_key_len = 65
        # MAC length (SHA-256 = 32 bytes)
        mac_len = 32
        
        if len(encrypted_bytes) < pub_key_len + mac_len + 16:
            logger.error(f"Encrypted data too short: {len(encrypted_bytes)} bytes")
            return None
        
        # Extract components
        ephemeral_pub_key = encrypted_bytes[:pub_key_len]
        mac_tag = encrypted_bytes[-mac_len:]
        em = encrypted_bytes[pub_key_len:-mac_len]
        
        logger.info(f"Ephemeral public key: {ephemeral_pub_key[:10].hex()}... ({len(ephemeral_pub_key)} bytes)")
        logger.info(f"Encrypted message: {len(em)} bytes")
        logger.info(f"MAC tag: {mac_tag[:10].hex()}... ({len(mac_tag)} bytes)")
        
        # Derive shared secret using ECDH
        shared_secret = private_key.ecdh(ephemeral_pub_key)
        logger.info(f"Derived shared secret: {shared_secret[:8].hex()}... ({len(shared_secret)} bytes)")
        
        # Derive keys using ConcatKDF (match Go implementation)
        key_len = 32  # AES-256
        s1 = b''    # Empty shared info for key derivation
        K = concat_kdf(hashlib.sha512, shared_secret, s1, 2 * key_len)
        encryption_key = K[:key_len]
        mac_key_raw = K[key_len:]
        
        h_inst = hashlib.sha256()
        h_inst.update(mac_key_raw)
        mac_key = h_inst.digest()
        
        logger.info(f"Derived encryption key: {encryption_key[:8].hex()}...")
        logger.info(f"Derived MAC key: {mac_key[:8].hex()}...")
        
        # Verify MAC - using full encrypted message (em) and empty s2
        h_mac = hmac.new(mac_key, digestmod=hashlib.sha256)
        h_mac.update(em)
        s2 = b''
        h_mac.update(s2)
        calculated_mac = h_mac.digest()
        
        logger.info(f"Calculated MAC: {calculated_mac[:10].hex()}...")
        logger.info(f"Expected MAC: {mac_tag[:10].hex()}...")
        
        if not hmac.compare_digest(mac_tag, calculated_mac):
            logger.error("MAC verification failed")
            # Try alternative method (without s2)
            h_mac = hmac.new(mac_key, digestmod=hashlib.sha256)
            h_mac.update(em)
            calculated_mac = h_mac.digest()
            logger.info(f"Alternative MAC (without s2): {calculated_mac[:10].hex()}...")
            if not hmac.compare_digest(mac_tag, calculated_mac):
                return None
            else:
                logger.info("MAC verification succeeded with alternative method")
        else:
            logger.info("MAC verification successful")
        
        # Decrypt using AES in CTR mode: format [IV][encrypted data]
        iv_size = 16  # AES block size
        iv = em[:iv_size]
        actual_ciphertext = em[iv_size:]
        
        cipher = AES.new(encryption_key, AES.MODE_CTR, nonce=iv)
        plaintext = cipher.decrypt(actual_ciphertext)
        
        logger.info(f"Decryption successful! Plaintext length: {len(plaintext)} bytes")
        return plaintext
        
    except Exception as e:
        logger.error(f"ECIES decryption error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def decrypt_alpha_message(private_key_hex: str, encrypted_message: dict) -> Optional[object]:
    """
    Decrypt a message using the AES key directly.
    
    Expects encrypted_message to contain 'aes_key' and 'encrypted_data' (both in hex).
    
    Returns:
        Decrypted data parsed as JSON (if possible) or as string.
    """
    try:
        aes_key_hex = encrypted_message.get('aes_key')
        encrypted_data_hex = encrypted_message.get('encrypted_data')
        
        if aes_key_hex and encrypted_data_hex:
            aes_key = bytes.fromhex(aes_key_hex)
            encrypted_data = bytes.fromhex(encrypted_data_hex)
            # In AES-GCM, format: [nonce (12 bytes)][ciphertext]
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt(ciphertext)
            text = plaintext.decode('utf-8', errors='replace')
            if '}' in text:
                json_end = text.rindex('}') + 1
                valid_json = text[:json_end]
                try:
                    result = json.loads(valid_json)
                    return result
                except json.JSONDecodeError:
                    return text
            else:
                return text
        logger.warning("No AES key provided in message")
        return None
    except Exception as e:
        logger.error(f"Message processing error: {e}")
        return None

def get_wallet_address(private_key: str) -> str:
    """
    Get Ethereum wallet address from private key.
    """
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    account = Account.from_key(private_key)
    return account.address

def get_public_key_from_private(private_key: str) -> dict:
    """
    Get public key information from a private key.
    
    Returns a dictionary with:
      - address: Ethereum wallet address
      - public_key: non-compressed public key as hex string
      - public_key_bytes: raw public key bytes
    """
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    account = Account.from_key(private_key)
    private_key_obj = keys.PrivateKey(binascii.unhexlify(private_key[2:]))
    public_key = private_key_obj.public_key
    public_key_bytes = public_key.to_bytes()
    public_key_hex = "0x" + public_key_bytes.hex()
    return {
        "address": account.address,
        "public_key": public_key_hex,
        "public_key_bytes": public_key_bytes
    }
