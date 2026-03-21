import os
import subprocess
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

class MinimalGitPuller:
    """Automated git pull with fetch-first optimization and animated UI."""

    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.found_repos = []
        self.results = {
            'updated': [],      # Repos that received changes
            'up_to_date': [],   # Repos already current
            'failed': [],       # Repos with errors
            'skipped': []       # Repos without remotes or no updates needed
        }

    # ... (rest of methods unchanged, but I must provide them as per instructions)

    def is_git_repo(self, path):
        git_dir = path / '.git'
        return git_dir.exists() and git_dir.is_dir()

    def find_git_repos(self, path, depth=0, max_depth=10):
        if depth > max_depth: return
        try:
            for item in path.iterdir():
                if item.name.startswith('.'): continue
                if item.is_dir():
                    if self.is_git_repo(item):
                        self.found_repos.append(item)
                    else:
                        self.find_git_repos(item, depth + 1, max_depth)
        except Exception: pass

    def has_remote(self, repo_path):
        try:
            result = subprocess.run(['git', '-C', str(repo_path), 'remote', '-v'], capture_output=True, text=True, timeout=5)
            return bool(result.stdout.strip())
        except Exception: return False

    def fetch_repo(self, repo_path):
        try:
            result = subprocess.run(['git', '-C', str(repo_path), 'fetch'], capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stderr.strip()
        except Exception as e: return False, str(e)

    def check_behind(self, repo_path):
        try:
            result = subprocess.run(['git', '-C', str(repo_path), 'rev-list', 'HEAD..@{u}', '--count'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return int(result.stdout.strip()) > 0, int(result.stdout.strip())
            return False, 0
        except Exception: return False, 0

    def pull_repo(self, repo_path):
        try:
            result = subprocess.run(['git', '-C', str(repo_path), 'pull'], capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout.strip()
        except Exception as e: return False, str(e)

    def process_repo(self, repo_path):
        relative_path = repo_path.relative_to(self.base_path)
        if not self.has_remote(repo_path):
            self.results['skipped'].append({'path': relative_path, 'reason': 'No remote'})
            return

        success, error = self.fetch_repo(repo_path)
        if not success:
            self.results['failed'].append({'path': relative_path, 'error': f"Fetch failed: {error}"})
            return

        is_behind, commit_count = self.check_behind(repo_path)
        if not is_behind:
            self.results['up_to_date'].append(relative_path)
            return

        success, message = self.pull_repo(repo_path)
        if success:
            self.results['updated'].append({'path': relative_path, 'commits': commit_count})
        else:
            self.results['failed'].append({'path': relative_path, 'error': f"Pull failed: {message}"})

    def run(self):
        start_time = datetime.now()
        print("=" * 60)
        print("  AUTO GIT PULL".center(60))
        print("=" * 60)
        print(f"📂 Base: {self.base_path}")
        self.find_git_repos(self.base_path)
        print(f"🔍 Found {len(self.found_repos)} repositories")

        for idx, repo in enumerate(self.found_repos, 1):
            print(f"\r🔄 Processing {idx}/{len(self.found_repos)}...", end="", flush=True)
            self.process_repo(repo)

        print("\n" + "=" * 60)
        if self.results['updated']:
            print(f"✅ UPDATED ({len(self.results['updated'])}):")
            for item in self.results['updated']: print(f"   • {item['path']} (+{item['commits']} commits)")

        if self.results['failed']:
            print(f"❌ FAILED ({len(self.results['failed'])}):")
            for item in self.results['failed']: print(f"   • {item['path']}: {item['error']}")

        print(f"⏩ UP TO DATE: {len(self.results['up_to_date'])} | ⚠️ SKIPPED: {len(self.results['skipped'])}")
        print(f"⏱️  Duration: {(datetime.now() - start_time).total_seconds():.1f}s")
        print("=" * 60)

def load_config():
    config_path = Path(__file__).parent / 'config.json'
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f).get('base_path')
    return None

def main():
    parser = argparse.ArgumentParser(description="Auto-pull updates for all Git repos in a directory.")
    parser.add_argument('--path', type=str, help="Directory to scan for Git repos")
    args = parser.parse_args()

    # Priority: 1. CLI Arg, 2. config.json, 3. Default (OneDrive)
    base_path = args.path or load_config() or str(Path.home() / 'OneDrive' / 'Desktop' / 'Public')

    if not os.path.exists(base_path):
        print(f"❌ Error: Path not found: {base_path}")
        sys.exit(1)

    puller = MinimalGitPuller(base_path)
    puller.run()
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()