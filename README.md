# operator-tool-sync
Python-based automation utility that synchronizes internal security tools between a GitLab repository and a local Linux system. The script authenticates to GitLab, pulls the latest tools from the repository, and uploads newly developed or updated tools back into the project to maintain centralized version control and streamline team collaboration.

NOTE: Ensure that Export is run in Linux CLI before execution of script

Example: 
export GITLAB_TOKEN="your_gitlab_token"
export GITLAB_REPO_URL="https://gitlab.com/your-group/your-repo.git"
