#!/usr/bin/env python3

# export GITLAB_TOKEN="your_gitlab_token"
# export GITLAB_REPO_URL="https://gitlab.com/your-group/your-repo.git"
# python3 gitlab_tool_sync.py

import os
import shutil
import subprocess
import sys
from pathlib import Path

# =========================
# CONFIG
# =========================
LOCAL_REPO_PATH = Path.home() / "internal_tools_repo"
LOCAL_TOOLS_PATH = Path.home() / "tools_local"
REPO_TOOLS_SUBDIR = Path("tools")

ALLOWED_EXT = [".py", ".sh", ".yaml", ".yml", ".json"]

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_REPO_URL = os.getenv("GITLAB_REPO_URL")

# =========================
# HELPERS
# =========================
def run_cmd(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[!] Command failed: {' '.join(cmd)}")
        print(f"[!] stdout:\n{e.stdout}")
        print(f"[!] stderr:\n{e.stderr}")
        sys.exit(1)

def ensure_env():
    if not GITLAB_TOKEN:
        print("[!] Missing GITLAB_TOKEN environment variable")
        sys.exit(1)

    if not GITLAB_REPO_URL:
        print("[!] Missing GITLAB_REPO_URL environment variable")
        sys.exit(1)

def build_auth_repo_url():
    if GITLAB_REPO_URL.startswith("https://"):
        return GITLAB_REPO_URL.replace("https://", f"https://oauth2:{GITLAB_TOKEN}@")
    print("[!] Only HTTPS GitLab repo URLs are supported in this script.")
    sys.exit(1)

def clone_or_pull_repo():
    auth_repo_url = build_auth_repo_url()

    if not LOCAL_REPO_PATH.exists():
        print(f"[*] Cloning repo into {LOCAL_REPO_PATH} ...")
        run_cmd(["git", "clone", auth_repo_url, str(LOCAL_REPO_PATH)])
    else:
        print(f"[*] Pulling latest changes in {LOCAL_REPO_PATH} ...")
        run_cmd(["git", "pull"], cwd=LOCAL_REPO_PATH)

def ensure_directories():
    LOCAL_TOOLS_PATH.mkdir(parents=True, exist_ok=True)
    (LOCAL_REPO_PATH / REPO_TOOLS_SUBDIR).mkdir(parents=True, exist_ok=True)

def download_tools_from_repo():
    repo_tools_dir = LOCAL_REPO_PATH / REPO_TOOLS_SUBDIR

    if not repo_tools_dir.exists():
        print(f"[!] Repo tools directory does not exist: {repo_tools_dir}")
        return

    print("[*] Downloading tools from repo to local system...")
    for item in repo_tools_dir.iterdir():
        dest = LOCAL_TOOLS_PATH / item.name

        if item.is_file():
            shutil.copy2(item, dest)
            print(f"[+] Copied file: {item.name}")
        elif item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
            print(f"[+] Copied directory: {item.name}")

def upload_new_tools_to_repo():
    repo_tools_dir = LOCAL_REPO_PATH / REPO_TOOLS_SUBDIR
    changed = False

    print("[*] Uploading local tools into repo...")
    for item in LOCAL_TOOLS_PATH.iterdir():
        dest = repo_tools_dir / item.name

        if item.is_file():
            if item.suffix not in ALLOWED_EXT:
                print(f"[-] Skipping unsupported file type: {item.name}")
                continue

            shutil.copy2(item, dest)
            print(f"[+] Uploaded file: {item.name}")
            changed = True

        elif item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
            print(f"[+] Uploaded directory: {item.name}")
            changed = True

    return changed

def commit_and_push():
    print("[*] Checking for git changes...")
    run_cmd(["git", "add", "."], cwd=LOCAL_REPO_PATH)

    status = run_cmd(["git", "status", "--porcelain"], cwd=LOCAL_REPO_PATH)
    if not status:
        print("[*] No changes detected. Nothing to commit.")
        return

    print("[*] Committing changes...")
    run_cmd(["git", "commit", "-m", "Sync internal tools via Python automation"], cwd=LOCAL_REPO_PATH)

    print("[*] Pushing changes to GitLab...")
    run_cmd(["git", "push"], cwd=LOCAL_REPO_PATH)

    print("[+] Changes pushed successfully.")

def main():
    ensure_env()
    clone_or_pull_repo()
    ensure_directories()
    download_tools_from_repo()
    changed = upload_new_tools_to_repo()

    if changed:
        commit_and_push()
    else:
        print("[*] No local tools found to upload.")

if __name__ == "__main__":
    main()
