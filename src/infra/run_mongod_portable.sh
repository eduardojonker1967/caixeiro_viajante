#!/usr/bin/env bash
# Portable helper to run MongoDB locally for development.
# - If `mongod` is installed on the system, starts it with a project-local dbpath.
# - Otherwise downloads a generic MongoDB Linux x86_64 tarball (6.0.x) and runs the bundled `mongod`.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DBPATH="$ROOT_DIR/mongo_data"
LOGFILE="$ROOT_DIR/mongo_log.log"
MONGO_DIR="$ROOT_DIR/mongodb_portable"
MONGO_TARBALL="$ROOT_DIR/mongodb-linux-x86_64.tgz"
MONGO_VERSION="6.0.14"
DOWNLOAD_BASE="https://fastdl.mongodb.org/linux"

mkdir -p "$DBPATH"

function start_system_mongod() {
    echo "Found system 'mongod' binary, starting with dbpath=$DBPATH"
    mkdir -p "$DBPATH"
    mongod --dbpath "$DBPATH" --bind_ip 127.0.0.1 --port 27017 --logpath "$LOGFILE" --fork
}

function start_portable_mongod() {
    echo "Starting portable mongod using binaries under $MONGO_DIR"
    mkdir -p "$MONGO_DIR"
    if [ ! -x "$MONGO_DIR/bin/mongod" ]; then
        echo "Downloading MongoDB $MONGO_VERSION (generic linux x86_64) to $MONGO_TARBALL"
        URL="$DOWNLOAD_BASE/mongodb-linux-x86_64-$MONGO_VERSION.tgz"
        echo "URL=$URL"
        curl -L "$URL" -o "$MONGO_TARBALL"
        echo "Extracting..."
        tar -xzf "$MONGO_TARBALL" -C "$ROOT_DIR"
        EXTRACTED_DIR=$(tar -tzf "$MONGO_TARBALL" | head -1 | cut -f1 -d"/")
        mv "$ROOT_DIR/$EXTRACTED_DIR" "$MONGO_DIR"
    fi

    echo "Running $MONGO_DIR/bin/mongod --dbpath $DBPATH ..."
    nohup "$MONGO_DIR/bin/mongod" --dbpath "$DBPATH" --bind_ip 127.0.0.1 --port 27017 --logpath "$LOGFILE" > /dev/null 2>&1 &
    sleep 1
}

if command -v mongod >/dev/null 2>&1; then
    start_system_mongod
else
    start_portable_mongod
fi

echo "Logs: $LOGFILE"
echo "MongoDB data directory: $DBPATH"
echo "Give it a second, then check with: python check_mongo_connection.py"
