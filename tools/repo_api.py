#!/usr/bin/env python3
"""
📁 Repo Service - File Operations & Git Management
Phase A: Core repository operations

Handles all file I/O, git operations, and code editing for the autonomous system.
"""

import os
import git
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import tempfile
import logging

logger = logging.getLogger(__name__)

@dataclass
class FileEdit:
    """Represents a file edit operation"""
    path: str
    mode: str  # create, replace, patch
    content: Optional[str] = None
    patch: Optional[str] = None

@dataclass
class RepoStatus:
    """Repository status information"""
    branch: str
    modified_files: List[str]
    untracked_files: List[str]
    staged_files: List[str]

class RepoService:
    """
    Handles all repository operations for the autonomous AI developer.
    
    Provides safe file operations, git management, and diff/patch capabilities.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo: Optional[git.Repo] = None
        
        # Ensure repo path exists
        self.repo_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize or open git repo
        self._init_git_repo()
        
        logger.info(f"📁 Repo service initialized at: {self.repo_path}")
    
    def _init_git_repo(self):
        """Initialize git repository if it doesn't exist"""
        try:
            self.repo = git.Repo(self.repo_path)
            logger.info(f"📁 Opened existing git repo")
        except git.exc.InvalidGitRepositoryError:
            # Initialize new repo
            self.repo = git.Repo.init(self.repo_path)
            
            # Create initial commit
            gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.coverage
.pytest_cache/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Autonomous AI Developer
.autopilot/
memory/states/
"""
            
            gitignore_path = self.repo_path / ".gitignore"
            gitignore_path.write_text(gitignore_content.strip())
            
            self.repo.index.add([".gitignore"])
            self.repo.index.commit("Initial commit - Autonomous AI Developer")
            
            logger.info(f"📁 Initialized new git repo")
    
    def read_files(self, paths: List[str], max_bytes: int = 200000) -> Dict[str, Any]:
        """
        Read files from the repository
        
        Args:
            paths: List of file paths (supports glob patterns)
            max_bytes: Maximum bytes to read per file
            
        Returns:
            Dictionary with file contents and metadata
        """
        import glob
        
        result = {
            "files": {},
            "total_files": 0,
            "total_bytes": 0,
            "truncated_files": []
        }
        
        try:
            # Expand glob patterns
            all_files = []
            for pattern in paths:
                if "*" in pattern or "?" in pattern:
                    # Glob pattern
                    matches = glob.glob(str(self.repo_path / pattern), recursive=True)
                    all_files.extend([Path(f).relative_to(self.repo_path) for f in matches])
                else:
                    # Direct path
                    all_files.append(Path(pattern))
            
            # Read each file
            for file_path in all_files:
                full_path = self.repo_path / file_path
                
                if not full_path.exists():
                    logger.warning(f"📁 File not found: {file_path}")
                    continue
                
                if full_path.is_dir():
                    continue
                
                try:
                    # Read file content
                    content = full_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Truncate if too large
                    if len(content.encode('utf-8')) > max_bytes:
                        content = content[:max_bytes] + "\n... [TRUNCATED]"
                        result["truncated_files"].append(str(file_path))
                    
                    result["files"][str(file_path)] = {
                        "content": content,
                        "size": full_path.stat().st_size,
                        "modified": full_path.stat().st_mtime
                    }
                    
                    result["total_files"] += 1
                    result["total_bytes"] += len(content.encode('utf-8'))
                    
                except Exception as e:
                    logger.error(f"📁 Error reading {file_path}: {e}")
                    result["files"][str(file_path)] = {"error": str(e)}
            
            logger.info(f"📁 Read {result['total_files']} files ({result['total_bytes']} bytes)")
            return result
            
        except Exception as e:
            logger.error(f"📁 Error in read_files: {e}")
            return {"error": str(e)}
    
    def write_files(self, edits: List[FileEdit], commit_message: str) -> Dict[str, Any]:
        """
        Write/edit files in the repository
        
        Args:
            edits: List of file edits to apply
            commit_message: Git commit message
            
        Returns:
            Result of the operation
        """
        result = {
            "success": True,
            "files_modified": [],
            "files_created": [],
            "errors": []
        }
        
        try:
            # Apply each edit
            for edit in edits:
                try:
                    file_path = self.repo_path / edit.path
                    
                    # Ensure parent directory exists
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if edit.mode == "create":
                        if file_path.exists():
                            result["errors"].append(f"File already exists: {edit.path}")
                            continue
                        
                        file_path.write_text(edit.content, encoding='utf-8')
                        result["files_created"].append(edit.path)
                        
                    elif edit.mode == "replace":
                        file_path.write_text(edit.content, encoding='utf-8')
                        if edit.path not in result["files_created"]:
                            result["files_modified"].append(edit.path)
                        
                    elif edit.mode == "patch":
                        if not file_path.exists():
                            result["errors"].append(f"Cannot patch non-existent file: {edit.path}")
                            continue
                        
                        # Apply unified diff patch
                        success = self._apply_patch(file_path, edit.patch)
                        if success:
                            result["files_modified"].append(edit.path)
                        else:
                            result["errors"].append(f"Failed to apply patch to: {edit.path}")
                    
                    logger.info(f"📁 {edit.mode.title()}: {edit.path}")
                    
                except Exception as e:
                    error_msg = f"Error editing {edit.path}: {e}"
                    result["errors"].append(error_msg)
                    logger.error(f"📁 {error_msg}")
            
            # Git add and commit if any files were modified
            modified_files = result["files_created"] + result["files_modified"]
            if modified_files and not result["errors"]:
                try:
                    self.repo.index.add(modified_files)
                    self.repo.index.commit(commit_message)
                    logger.info(f"📁 Committed {len(modified_files)} files: {commit_message}")
                except Exception as e:
                    result["errors"].append(f"Git commit failed: {e}")
                    result["success"] = False
            
            if result["errors"]:
                result["success"] = False
            
            return result
            
        except Exception as e:
            logger.error(f"📁 Error in write_files: {e}")
            return {"success": False, "error": str(e)}
    
    def _apply_patch(self, file_path: Path, patch_content: str) -> bool:
        """Apply a unified diff patch to a file"""
        try:
            # Create temporary patch file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
                f.write(patch_content)
                patch_file = f.name
            
            try:
                # Apply patch using git apply
                subprocess.run([
                    "git", "apply", "--check", patch_file
                ], cwd=self.repo_path, check=True, capture_output=True)
                
                subprocess.run([
                    "git", "apply", patch_file
                ], cwd=self.repo_path, check=True, capture_output=True)
                
                return True
                
            finally:
                # Clean up temp file
                os.unlink(patch_file)
                
        except subprocess.CalledProcessError as e:
            logger.error(f"📁 Patch application failed: {e.stderr.decode()}")
            return False
        except Exception as e:
            logger.error(f"📁 Patch error: {e}")
            return False
    
    def get_status(self) -> RepoStatus:
        """Get current repository status"""
        try:
            return RepoStatus(
                branch=self.repo.active_branch.name,
                modified_files=[item.a_path for item in self.repo.index.diff(None)],
                untracked_files=self.repo.untracked_files,
                staged_files=[item.a_path for item in self.repo.index.diff("HEAD")]
            )
        except Exception as e:
            logger.error(f"📁 Error getting repo status: {e}")
            return RepoStatus(branch="unknown", modified_files=[], untracked_files=[], staged_files=[])
    
    def create_branch(self, branch_name: str) -> bool:
        """Create and switch to a new branch"""
        try:
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            logger.info(f"📁 Created and switched to branch: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"📁 Error creating branch {branch_name}: {e}")
            return False
    
    def switch_branch(self, branch_name: str, create: bool = True) -> bool:
        """Switch to an existing branch or create new one"""
        try:
            # Check if branch exists
            if branch_name in [b.name for b in self.repo.branches]:
                self.repo.heads[branch_name].checkout()
                logger.info(f"📁 Switched to existing branch: {branch_name}")
                return True
            elif create:
                return self.create_branch(branch_name)
            else:
                logger.error(f"📁 Branch {branch_name} does not exist")
                return False
        except Exception as e:
            logger.error(f"📁 Error switching to branch {branch_name}: {e}")
            return False
    
    def get_diff(self, commit1: str = None, commit2: str = None) -> str:
        """Get diff between commits or working directory"""
        try:
            if commit1 and commit2:
                diff = self.repo.git.diff(commit1, commit2)
            elif commit1:
                diff = self.repo.git.diff(commit1)
            else:
                diff = self.repo.git.diff()
            
            return diff
        except Exception as e:
            logger.error(f"📁 Error getting diff: {e}")
            return ""
    
    def search_files(self, query: str, file_patterns: List[str] = None) -> List[Dict[str, Any]]:
        """Search for text in files"""
        import re
        
        results = []
        
        try:
            # Default to common code files if no patterns specified
            if not file_patterns:
                file_patterns = ["*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.h", "*.md", "*.txt"]
            
            # Get all matching files
            files_to_search = []
            for pattern in file_patterns:
                files_to_search.extend(self.repo_path.glob(f"**/{pattern}"))
            
            # Search in each file
            for file_path in files_to_search:
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            if re.search(query, line, re.IGNORECASE):
                                results.append({
                                    "file": str(file_path.relative_to(self.repo_path)),
                                    "line": line_num,
                                    "content": line.strip(),
                                    "match": query
                                })
                    except Exception as e:
                        logger.warning(f"📁 Error searching {file_path}: {e}")
            
            logger.info(f"📁 Found {len(results)} matches for '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"📁 Error in search: {e}")
            return []

# Test the repo service
def test_repo_service():
    """Test the repo service functionality"""
    print("🧪 Testing Repo Service...")
    
    # Create test repo
    test_path = Path("test_repo")
    if test_path.exists():
        shutil.rmtree(test_path)
    
    repo = RepoService(str(test_path))
    
    # Test file creation
    edits = [
        FileEdit(path="test.py", mode="create", content="print('Hello, World!')"),
        FileEdit(path="src/main.py", mode="create", content="def main():\n    pass")
    ]
    
    result = repo.write_files(edits, "Initial test files")
    print(f"✅ Write result: {result['success']}, created: {result['files_created']}")
    
    # Test file reading
    read_result = repo.read_files(["*.py", "src/*.py"])
    print(f"✅ Read {read_result['total_files']} files")
    
    # Test search
    search_results = repo.search_files("Hello")
    print(f"✅ Found {len(search_results)} search matches")
    
    # Test status
    status = repo.get_status()
    print(f"✅ Repo status - branch: {status.branch}")
    
    # Cleanup
    shutil.rmtree(test_path)
    print("🧪 Repo Service test completed!")

if __name__ == "__main__":
    test_repo_service()