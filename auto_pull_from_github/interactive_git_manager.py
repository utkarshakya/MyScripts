import os
import subprocess
import sys
from pathlib import Path


class GitRepoManager:
    """Interactive Git Repository Manager for navigating and managing repositories."""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.current_path = self.base_path
        self.path_history = []
    
    def is_git_repo(self, path):
        """Check if a directory is a git repository."""
        git_dir = path / '.git'
        return git_dir.exists() and git_dir.is_dir()
    
    def get_git_info(self, path):
        """Get current branch and status of a git repository."""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ['git', '-C', str(path), 'branch', '--show-current'],
                capture_output=True,
                text=True,
                timeout=5
            )
            branch = branch_result.stdout.strip() or 'detached HEAD'
            
            # Check for uncommitted changes
            status_result = subprocess.run(
                ['git', '-C', str(path), 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=5
            )
            has_changes = bool(status_result.stdout.strip())
            
            return branch, has_changes
        except Exception as e:
            return None, None
    
    def list_directories(self):
        """List all directories in the current path with git indicators."""
        try:
            items = []
            for item in sorted(self.current_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    is_git = self.is_git_repo(item)
                    info = {'path': item, 'name': item.name, 'is_git': is_git}
                    
                    if is_git:
                        branch, has_changes = self.get_git_info(item)
                        info['branch'] = branch
                        info['has_changes'] = has_changes
                    
                    items.append(info)
            return items
        except PermissionError:
            print(f"\n❌ Permission denied: Cannot access {self.current_path}")
            return []
    
    def display_folders(self, items):
        """Display folders with git information."""
        if not items:
            print("\n📂 No folders found in this directory.")
            return
        
        print(f"\n📍 Current location: {self.current_path}")
        print("=" * 80)
        
        for idx, item in enumerate(items, 1):
            if item['is_git']:
                git_info = f"[GIT: {item['branch']}"
                if item['has_changes']:
                    git_info += " - UNCOMMITTED CHANGES"
                git_info += "]"
                print(f"{idx}. {item['name']:<40} {git_info}")
            else:
                print(f"{idx}. {item['name']:<40} [FOLDER]")
        
        print("=" * 80)
    
    def git_pull(self, path):
        """Perform git pull operation."""
        print(f"\n🔄 Pulling changes for: {path.name}")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                ['git', '-C', str(path), 'pull'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Pull successful!")
                print(result.stdout)
            else:
                print("❌ Pull failed!")
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print("❌ Pull operation timed out (30 seconds).")
        except Exception as e:
            print(f"❌ Error during pull: {str(e)}")
        
        print("-" * 60)
    
    def open_in_explorer(self, path):
        """Open folder in Windows File Explorer."""
        try:
            subprocess.run(['explorer', str(path)])
            print(f"✅ Opened {path.name} in File Explorer")
        except Exception as e:
            print(f"❌ Failed to open in File Explorer: {str(e)}")
    
    def navigate_to(self, path):
        """Navigate to a new directory."""
        self.path_history.append(self.current_path)
        self.current_path = path
    
    def go_back(self):
        """Go back to the previous directory."""
        if self.path_history:
            self.current_path = self.path_history.pop()
            return True
        return False
    
    def show_breadcrumb(self):
        """Display breadcrumb trail of navigation history."""
        if self.path_history:
            print("\n🔖 Navigation trail:")
            trail = " → ".join([p.name for p in self.path_history])
            print(f"   {trail} → {self.current_path.name}")
    
    def run(self):
        """Main interactive loop."""
        print("=" * 80)
        print("🚀 GIT REPOSITORY MANAGER".center(80))
        print("=" * 80)
        
        while True:
            items = self.list_directories()
            self.display_folders(items)
            self.show_breadcrumb()
            
            print("\n📋 Options:")
            if items:
                print("   • Enter folder number to select")
            if self.path_history:
                print("   • Type 'b' or 'back' to go to parent folder")
            print("   • Type 'h' or 'home' to return to base folder")
            print("   • Type 'q' or 'quit' to exit")
            
            choice = input("\n👉 Your choice: ").strip().lower()
            
            # Handle quit
            if choice in ['q', 'quit', 'exit']:
                print("\n👋 Goodbye!")
                break
            
            # Handle back
            if choice in ['b', 'back']:
                if self.go_back():
                    print("✅ Moved to parent folder")
                else:
                    print("❌ Already at base folder")
                continue
            
            # Handle home
            if choice in ['h', 'home']:
                self.current_path = self.base_path
                self.path_history.clear()
                print("✅ Returned to base folder")
                continue
            
            # Handle folder selection
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    selected = items[idx]
                    
                    if selected['is_git']:
                        # Git repository - show actions
                        print(f"\n📦 Selected: {selected['name']} (Git Repository)")
                        print(f"   Branch: {selected['branch']}")
                        if selected['has_changes']:
                            print("   ⚠️  Has uncommitted changes")
                        
                        print("\n   1. Pull from remote")
                        print("   2. Open in File Explorer")
                        print("   3. Navigate into folder")
                        print("   4. Cancel")
                        
                        action = input("\n   Choose action (1-4): ").strip()
                        
                        if action == '1':
                            self.git_pull(selected['path'])
                            input("\nPress Enter to continue...")
                        elif action == '2':
                            self.open_in_explorer(selected['path'])
                        elif action == '3':
                            self.navigate_to(selected['path'])
                        elif action == '4':
                            print("   Cancelled")
                        else:
                            print("   ❌ Invalid action")
                    else:
                        # Regular folder - navigate into it
                        self.navigate_to(selected['path'])
                        print(f"✅ Navigated to: {selected['name']}")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a valid number or command")


def main():
    """Entry point for the interactive script."""
    # Get the Public folder on Desktop
    desktop = Path.home() / 'OneDrive' / 'Desktop'
    public_folder = desktop / 'Public'
    
    # Check if Public folder exists
    if not public_folder.exists():
        print(f"❌ Error: Public folder not found at {public_folder}")
        print("   Please create the folder or update the path in the script.")
        sys.exit(1)
    
    if not public_folder.is_dir():
        print(f"❌ Error: {public_folder} is not a directory")
        sys.exit(1)
    
    # Run the manager
    manager = GitRepoManager(public_folder)
    manager.run()


if __name__ == "__main__":
    main()
