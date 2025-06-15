#!/bin/bash

# AWS region and secret name
region="us-east-1"
keyname="tenx/env/vars"

# Optional AWS profile handling
prof=""
if [ -f ~/.aws/config ]; then
    if grep -q tenac ~/.aws/config; then
        prof="--profile tenac"  # Adjust profile name if needed
    fi
fi

# Secret retrieval function
function get_ssm_secret() {
    aws secretsmanager get-secret-value \
        --secret-id "$1" \
        --query SecretString \
        --output text \
        --region "$region" $prof 2>/dev/null
}

# Root dir detection
curdir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
efs_path="/mnt/efs/leap"

if [ ! -d "${efs_path}" ]; then
    rootdir=$(dirname "$curdir")
else
    rootdir="${efs_path}"
fi

# Setup .env path
envdir="$rootdir/.env"
mkdir -p "$envdir"
envfile="$envdir/.envdev"

# Load or fetch .env content
if [ ! -f "$envfile" ]; then
    echo "Reading $keyname from AWS Secrets Manager..."

    secret_json=$(get_ssm_secret "$keyname")

    if [ -z "$secret_json" ]; then
        echo "❌ Failed to retrieve secret or secret is empty."
        exit 1
    fi

    # Convert JSON to KEY=VALUE format using jq
    parsed_env=$(echo "$secret_json" | jq -r 'to_entries | map("\(.key)=\(.value|tostring)") | .[]')

    # Save and export
    > "$envfile"  # clear if exists
    while IFS= read -r line; do
        echo "$line" >> "$envfile"
        export "$line"
    done <<< "$parsed_env"

    echo "✅ Secret values saved and exported from $envfile"
else
    echo "Using existing $envfile"
    set -a
    source "$envfile"
    set +a
fi
