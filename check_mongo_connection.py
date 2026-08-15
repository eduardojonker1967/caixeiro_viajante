#!/usr/bin/env python3
"""Quick diagnostic for MongoDB connectivity.

Usage:
  python check_mongo_connection.py

It reads MONGO_URI from environment (default mongodb://localhost:27017/),
resolves DNS, checks TCP connect to host:port and (optionally) tries a
`pymongo` server_info() call to exercise the MongoDB handshake.
"""
import os
import socket
import sys
from urllib.parse import urlparse

DEFAULT = "mongodb://localhost:27017/"

def parse_mongo_uri(uri):
    parsed = urlparse(uri)
    host = parsed.hostname or 'localhost'
    port = parsed.port or 27017
    return host, port

def check_tcp(host, port, timeout=5):
    try:
        print(f"Resolving {host}...")
        infos = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        addr = infos[0][4]
        print(f" -> Resolved to {addr}")
    except Exception as e:
        print(f"DNS resolution failed: {e}")
        return False

    try:
        print(f"Checking TCP connect to {host}:{port} (timeout={timeout}s)...")
        with socket.create_connection((host, port), timeout=timeout):
            print("TCP connection: OK")
            return True
    except Exception as e:
        print(f"TCP connection failed: {e}")
        return False

def check_pymongo(uri):
    try:
        from pymongo import MongoClient
    except Exception as e:
        print(f"pymongo not installed or import failed: {e}")
        return False

    try:
        print("Attempting pymongo server_info() handshake...")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        info = client.server_info()
        print("pymongo handshake: OK")
        print(f"MongoDB version: {info.get('version')}")
        return True
    except Exception as e:
        print(f"pymongo handshake failed: {e}")
        return False

def main():
    uri = os.getenv('MONGO_URI', DEFAULT)
    print(f"Using MONGO_URI={uri}")
    host, port = parse_mongo_uri(uri)

    tcp_ok = check_tcp(host, port)
    pymongo_ok = False
    if tcp_ok:
        pymongo_ok = check_pymongo(uri)

    print('\nSummary:')
    print(f" - TCP connection: {'OK' if tcp_ok else 'FAILED'}")
    print(f" - pymongo handshake: {'OK' if pymongo_ok else 'FAILED or SKIPPED'}")

    if not tcp_ok:
        print('\nHints:')
        print(" - If you use Docker Compose, run: docker compose up -d mongodb")
        print(" - To run Mongo locally: sudo apt install -y mongodb-org (or use distro package)")
        print(" - Check firewall or that the host:port are reachable from this machine.")
        sys.exit(2)

    if not pymongo_ok:
        print('\nHint: pymongo failed; try installing with: pip install pymongo')
        sys.exit(3)

    print('\nAll checks passed — pymongo can reach MongoDB')

if __name__ == '__main__':
    main()
