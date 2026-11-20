"""Deploy the app to Hugging Face Spaces in one step.

Reads three values from .env (or the environment):
    OPENROUTER_API_KEY  your OpenRouter key; stored on Hugging Face as a private Space secret
    HF_TOKEN            a Hugging Face access token with "write" permission
    HF_SPACE            the Space name, e.g. property-assistant (or username/property-assistant)

Then it creates the Space if needed (Docker SDK, public), uploads the code and data,
sets the key as a secret, restarts the Space, waits for the build and checks /api/health.
.env itself is never uploaded.

Usage: python scripts/deploy_hf.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

try:
    from huggingface_hub import HfApi
except ImportError:
    sys.exit("Missing package: run  pip install huggingface_hub  (or bash scripts/pipeline.sh first).")

ROOT = Path(__file__).resolve().parent.parent
NEVER_UPLOAD = [".env", ".env.local", ".venv/**", "**/__pycache__/**", "**/*.pyc", ".pytest_cache/**",
                ".git/**", "*.zip", ".pipeline-server.log", ".DS_Store", "**/.DS_Store"]
REPLACE_DIRS = ["app/**", "data/**", "scraper/**", "tests/**", "scripts/**"]  # stale files here are removed


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def setting(name: str, env: dict[str, str]) -> str:
    return (os.getenv(name) or env.get(name) or "").strip()


def main() -> None:
    env = read_env(ROOT / ".env")
    key, token, space = setting("OPENROUTER_API_KEY", env), setting("HF_TOKEN", env), setting("HF_SPACE", env)
    missing = [n for n, v in [("OPENROUTER_API_KEY", key), ("HF_TOKEN", token), ("HF_SPACE", space)] if not v]
    if missing:
        sys.exit(f"Add {', '.join(missing)} to .env (see .env.example), save, and run this again.")

    api = HfApi(token=token)
    user = api.whoami()["name"]
    repo_id = space if "/" in space else f"{user}/{space}"
    print(f"Signed in to Hugging Face as {user}. Deploying to Space {repo_id}")

    api.create_repo(repo_id, repo_type="space", space_sdk="docker", exist_ok=True, private=False)
    print("Uploading code and data (.env is excluded)...")
    api.upload_folder(
        repo_id=repo_id,
        repo_type="space",
        folder_path=ROOT,
        commit_message="Deploy property assistant",
        ignore_patterns=NEVER_UPLOAD,
        delete_patterns=REPLACE_DIRS,
    )

    api.add_space_secret(repo_id, "OPENROUTER_API_KEY", key, description="OpenRouter key for the chatbot")
    models = setting("OPENROUTER_MODELS", env)
    if models:
        api.add_space_variable(repo_id, "OPENROUTER_MODELS", models)
    host = getattr(api.space_info(repo_id), "host", None) or f"https://{repo_id.replace('/', '-').replace('_', '-').lower()}.hf.space"
    api.add_space_variable(repo_id, "APP_URL", host)
    print("Key saved as a private Space secret. Restarting the Space...")
    api.restart_space(repo_id)

    print("Waiting for the build (usually 2-5 minutes)...")
    last = None
    for _ in range(120):
        stage = getattr(api.get_space_runtime(repo_id), "stage", None)
        if stage != last:
            print(f"  status: {stage}")
            last = stage
        if stage == "RUNNING":
            break
        if stage in {"BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR", "NO_APP_FILE"}:
            sys.exit(f"The Space reported {stage}. Open https://huggingface.co/spaces/{repo_id} and check the Logs tab.")
        time.sleep(5)

    try:
        with urllib.request.urlopen(f"{host}/api/health", timeout=20) as resp:
            health = json.load(resp)
        print("Health:", health)
        if not health.get("llm_enabled"):
            print("Warning: the key isn't reaching the app. Check the secret in the Space settings.")
    except Exception as exc:  # the page can take a few seconds after RUNNING
        print(f"Couldn't reach {host}/api/health yet ({exc}). Try it in your browser in a minute.")

    print(f"\nLive URL: {host}\nSpace page: https://huggingface.co/spaces/{repo_id}")


if __name__ == "__main__":
    main()
