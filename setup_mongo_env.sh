#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
EXAMPLE_FILE="$PROJECT_ROOT/.env.example"
DEFAULT_USER="root"

function usage() {
  cat <<EOF
Usage: $0 [mongo_root_user]

Generates a secure MongoDB root password and writes it to .env.
If .env already exists, use --force to overwrite.

Examples:
  $0
  $0 admin
  $0 --force admin
EOF
}

FORCE=false
USER="$DEFAULT_USER"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force|-f)
      FORCE=true
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      USER="$1"
      shift
      ;;
  esac
done

if [[ ! -f "$EXAMPLE_FILE" ]]; then
  echo "❌ .env.example not found in $PROJECT_ROOT"
  exit 1
fi

if [[ -f "$ENV_FILE" && "$FORCE" != true ]]; then
  echo "❌ .env already exists. Use --force to overwrite it."
  echo "   Existing file: $ENV_FILE"
  exit 1
fi

PASSWORD=$(python - <<'PY'
import secrets
import string
alphabet = string.ascii_letters + string.digits
print(''.join(secrets.choice(alphabet) for _ in range(24)))
PY
)

cat > "$ENV_FILE" <<EOF
MONGO_ROOT_USER=$USER
MONGO_ROOT_PASSWORD=$PASSWORD
EOF

chmod 600 "$ENV_FILE"

echo "✅ Created $ENV_FILE"
echo "   MONGO_ROOT_USER=$USER"
echo "   MONGO_ROOT_PASSWORD is generated securely"
echo
 echo "Next steps:"
echo "  1) If you already have a Mongo volume, run: docker compose down -v"
echo "  2) Start MongoDB: docker compose up -d mongodb"
echo "  3) Verify: python check_mongo_connection.py"
