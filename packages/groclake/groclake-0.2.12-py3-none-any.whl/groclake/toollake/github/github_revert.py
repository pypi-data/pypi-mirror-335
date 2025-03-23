import os
import requests
from dotenv import load_dotenv

class GitHubRevert:
    def __init__(self, owner, repo, github_token=None):
        """
        Initialize the GitHubRevert class with repository details.
        
        Args:
            owner (str): GitHub repository owner/username
            repo (str): GitHub repository name
            github_token (str, optional): GitHub personal access token. If None, will try to load from environment.
        """
        self.owner = owner
        self.repo = repo
        
        # Load token from argument or environment
        if github_token:
            self.github_token = github_token
        else:
            load_dotenv()
            self.github_token = os.getenv("GITHUB_TOKEN")
            
        if not self.github_token:
            raise ValueError("GitHub token not provided and not found in environment variables")
            
        # Set up API headers
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_last_merged_pr(self):
        """Get the last merged pull request in the repository."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls?state=closed&sort=updated&direction=desc"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            prs = response.json()
            for pr in prs:
                if pr.get("merged_at"):
                    return pr
        
        print("No merged PRs found.")
        return None

    def branch_exists(self, branch_name):
        """Check if a branch exists in the repository."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200

    def delete_branch(self, branch_name):
        """Delete a branch from the repository."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 204

    def create_branch(self, branch_name, base_sha):
        """Create a new branch in the repository."""
        if self.branch_exists(branch_name):
            print(f"Branch '{branch_name}' already exists. Deleting it...")
            if not self.delete_branch(branch_name):
                print(f"Failed to delete branch '{branch_name}'.")
                return False
        
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs"
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 201:
            print(f"Branch '{branch_name}' created successfully.")
            return True
        else:
            print(f"Failed to create branch: {response.json()}")
            return False

    def get_commit_details(self, commit_sha):
        """Get details of a specific commit."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{commit_sha}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch commit details: {response.json()}")
            return None
        
        return response.json()

    def create_revert_commit(self, branch_name, merge_commit_sha):
        """Create a commit that reverts changes from a merge commit."""
        commit_data = self.get_commit_details(merge_commit_sha)
        if not commit_data:
            return False

        parent_sha = commit_data["parents"][0]["sha"]
        parent_commit_data = self.get_commit_details(parent_sha)
        if not parent_commit_data:
            return False
        
        parent_tree_sha = parent_commit_data["commit"]["tree"]["sha"]
        
        revert_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/commits"
        revert_payload = {
            "message": f"Revert PR changes from commit {merge_commit_sha}",
            "parents": [commit_data["sha"]],
            "tree": parent_tree_sha
        }

        revert_response = requests.post(revert_url, json=revert_payload, headers=self.headers)
        
        if revert_response.status_code != 201:
            print(f"Failed to create revert commit: {revert_response.json()}")
            return False

        revert_commit_sha = revert_response.json()["sha"]
        
        update_branch_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
        update_payload = {
            "sha": revert_commit_sha,
            "force": True
        }
        update_response = requests.patch(update_branch_url, json=update_payload, headers=self.headers)
        
        if update_response.status_code == 200:
            print(f"Branch '{branch_name}' updated with correct revert commit.")
            return True
        else:
            print(f"Failed to update branch: {update_response.json()}")
            return False

    def create_revert_pr(self, branch_name, pr):
        """Create a pull request to revert changes."""
        pr_number = pr["number"]
        pr_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls"
        payload = {
            "title": f"Revert PR #{pr_number}",
            "head": f"{self.owner}:{branch_name}",
            "base": "main",
            "body": f"This PR reverts the changes from PR #{pr_number}."
        }
        response = requests.post(pr_url, json=payload, headers=self.headers)
        
        if response.status_code == 201:
            pr_data = response.json()
            print(f"Revert PR created: {pr_data['html_url']}")
            return pr_data["number"]
        else:
            print(f"Failed to create revert PR: {response.json()}")
            return None

    def automerge_pr(self, pr_number):
        """Automatically merge a pull request."""
        merge_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_number}/merge"
        merge_payload = {"commit_title": f"Auto-merging PR #{pr_number}"}
        response = requests.put(merge_url, json=merge_payload, headers=self.headers)
        
        if response.status_code == 200:
            print(f"PR #{pr_number} merged successfully.")
            return True
        else:
            print(f"Failed to merge PR: {response.json()}")
            return False

    def revert_pr(self, pr_number=None):
        """
        Revert a specific PR by number, or the last merged PR if no number provided.
        
        Args:
            pr_number (int, optional): PR number to revert. If None, reverts the last merged PR.
            
        Returns:
            bool: True if revert was successful, False otherwise
        """
        if pr_number:
            # Get specific PR details
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200 or not response.json().get("merged"):
                print(f"PR #{pr_number} not found or not merged.")
                return False
            pr = response.json()
        else:
            # Get last merged PR
            pr = self.get_last_merged_pr()
            
        if not pr:
            return False
        
        pr_number = pr["number"]
        merge_commit_sha = pr["merge_commit_sha"]
        branch_name = f"revert-pr-{pr_number}"

        # Get main branch SHA
        main_branch_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/main"
        main_response = requests.get(main_branch_url, headers=self.headers)
        
        if main_response.status_code != 200:
            print(f"Failed to fetch main branch details: {main_response.json()}")
            return False
        
        main_sha = main_response.json()["object"]["sha"]
        
        # Create branch, revert commit, create PR and merge
        if not self.create_branch(branch_name, main_sha):
            return False
        
        if not self.create_revert_commit(branch_name, merge_commit_sha):
            return False
        
        new_pr_id = self.create_revert_pr(branch_name, pr)
        if not new_pr_id:
            return False
        
        return self.automerge_pr(new_pr_id)
