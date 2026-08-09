import os
import subprocess
import json
from typing import Dict, Any, Optional, List
try:
    from github import Github, GithubException
except ImportError:
    Github = None  # Fallback check handled during instantiation


class GitHubWorkflowManager:
    """
    Automated GitHub & Local Git Manager for Saphira.
    Handles reading repos, branch creation, auto-committing, pushing, and PR creation.
    """

    def __init__(self, github_token: Optional[str] = None, local_repo_path: str = "."):
        self.token = github_token or os.getenv("GITHUB_TOKEN")
        self.local_repo_path = os.path.abspath(local_repo_path)
        self.gh_client = Github(self.token) if (Github and self.token) else None

    # --- Local Git Operations ---

    def _run_git_cmd(self, args: List[str]) -> str:
        """Helper to run local Git commands safely."""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.local_repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    def create_feature_branch(self, branch_name: str) -> str:
        """Creates and switches to a new feature branch locally."""
        try:
            self._run_git_cmd(["checkout", "-b", branch_name])
            return f"Successfully created and switched to branch '{branch_name}'."
        except subprocess.CalledProcessError as e:
            return f"Failed to create branch: {e.stderr}"

    def commit_and_push(self, commit_message: str, branch_name: str, files: Optional[List[str]] = None) -> str:
        """Stages specified files (or all changes), commits, and pushes to remote."""
        try:
            if files:
                for file in files:
                    self._run_git_cmd(["add", file])
            else:
                self._run_git_cmd(["add", "."])

            self._run_git_cmd(["commit", "-m", commit_message])
            self._run_git_cmd(["push", "-u", "origin", branch_name])
            return f"Changes committed with message '{commit_message}' and pushed to '{branch_name}'."
        except subprocess.CalledProcessError as e:
            return f"Git operation failed: {e.stderr}"

    def inspect_repo_structure(self, max_depth: int = 2) -> Dict[str, Any]:
        """Scans local repo directory structure for automated analysis and context mapping."""
        tree = {}
        start_dir = self.local_repo_path
        
        for root, dirs, files in os.walk(start_dir):
            # Ignore hidden files, .git, and venvs
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__")]
            
            rel_path = os.path.relpath(root, start_dir)
            depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1
            
            if depth > max_depth:
                continue

            current = tree
            if rel_path != ".":
                for part in rel_path.split(os.sep):
                    current = current.setdefault(part, {})

            for file in files:
                if not file.startswith("."):
                    current[file] = "file"

        return tree

    # --- Remote GitHub Operations ---

    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """Opens a Pull Request on GitHub for the specified repository."""
        if not self.gh_client:
            return {"status": "error", "message": "GitHub API token not configured or PyGithub missing."}

        try:
            repo = self.gh_client.get_repo(repo_name)
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            return {
                "status": "success",
                "pr_number": pr.number,
                "pr_url": pr.html_url
            }
        except GithubException as e:
            return {"status": "error", "message": f"GitHub API error: {e.data.get('message', str(e))}"}

    def generate_and_save_readme(self, project_name: str, summary: str, features: List[str]) -> str:
        """Auto-generates a standardized README.md for the repository."""
        readme_content = f"# {project_name}\n\n"
        readme_content += f"{summary}\n\n"
        readme_content += "## Core Features\n"
        for feat in features:
            readme_content += f"- {feat}\n"
        
        readme_content += "\n\n---\n*Generated automatically by Saphira AI Workflow Manager.*"

        readme_path = os.path.join(self.local_repo_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        return f"README.md successfully written to {readme_path}"


# --- Integration with Saphira's Plugin Registry ---

def register_github_tools(registry, gh_manager: GitHubWorkflowManager):
    """Binds the GitHub workflow methods to Saphira's Plugin Registry."""

    @registry.register_tool(
        name="git_create_branch",
        description="Creates and checks out a new local git feature branch."
    )
    async def git_create_branch(branch_name: str) -> str:
        return gh_manager.create_feature_branch(branch_name)

    @registry.register_tool(
        name="git_commit_and_push",
        description="Stages files, commits changes, and pushes branch to origin."
    )
    async def git_commit_and_push(commit_message: str, branch_name: str, files: Optional[List[str]] = None) -> str:
        return gh_manager.commit_and_push(commit_message, branch_name, files)

    @registry.register_tool(
        name="github_create_pr",
        description="Creates a Pull Request on remote GitHub repository."
    )
    async def github_create_pr(repo_name: str, title: str, body: str, head_branch: str, base_branch: str = "main") -> dict:
        return gh_manager.create_pull_request(repo_name, title, body, head_branch, base_branch)

    @registry.register_tool(
        name="inspect_repo_structure",
        description="Scans directory tree to analyze local workspace layout."
    )
    async def inspect_repo_structure(max_depth: int = 2) -> dict:
        return gh_manager.inspect_repo_structure(max_depth=max_depth)

