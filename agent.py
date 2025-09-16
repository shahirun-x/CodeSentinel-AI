# agent.py
import requests
import os
import json
import base64

# --- Constants ---
REPO_OWNER = "shahirun-x"
REPO_NAME = "CodeSentinel-AI"
BASE_BRANCH = "main"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

def create_new_branch(new_branch_name, token):
    # ... (this function is the same, no changes) ...
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    ref_url = f"{GITHUB_API_URL}/git/ref/heads/{BASE_BRANCH}"
    response = requests.get(ref_url, headers=headers)
    if response.status_code != 200: return False
    base_sha = response.json()['object']['sha']
    print(f"-> Getting latest commit... Success.")
    print(f"-> Creating new branch '{new_branch_name}'...")
    new_ref_url = f"{GITHUB_API_URL}/git/refs"
    payload = {"ref": f"refs/heads/{new_branch_name}", "sha": base_sha}
    response = requests.post(new_ref_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 201:
        print(f"   Success! Branch created.")
        return True
    else:
        if "Reference already exists" in response.json().get('message', ''):
             print(f"   Info: Branch already exists. Continuing.")
             return True
        print(f"!! Error creating branch: {response.json()}")
        return False

def update_requirements_file(branch_name, package_to_update, new_version, token):
    # ... (this function is the same, no changes) ...
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    file_path = "requirements.txt"
    url = f"{GITHUB_API_URL}/contents/{file_path}?ref={BASE_BRANCH}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200: return False
    file_data = response.json()
    file_content = base64.b64decode(file_data['content']).decode('utf-8')
    file_sha = file_data['sha']
    print(f"-> Getting content of '{file_path}'... Success.")
    updated_lines = []
    found_package = False
    for line in file_content.splitlines():
        if line.lower().startswith(package_to_update.lower()):
            updated_lines.append(f"{package_to_update}=={new_version}")
            found_package = True
        else:
            updated_lines.append(line)
    if not found_package: return False
    updated_content_b64 = base64.b64encode("\n".join(updated_lines).encode('utf-8')).decode('utf-8')
    print(f"-> Committing updated '{file_path}' to '{branch_name}'...")
    commit_url = f"{GITHUB_API_URL}/contents/{file_path}"
    payload = {"message": f"feat: Upgrade {package_to_update} to {new_version}", "content": updated_content_b64, "sha": file_sha, "branch": branch_name}
    response = requests.put(commit_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print(f"   Success! Committed change.")
        return True
    else:
        print(f"!! Error committing change: {response.json()}")
        return False

# --- NEW FUNCTION ---
def create_pull_request(head_branch, title, body, token):
    """
    Creates a new pull request on GitHub.
    """
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    pr_url = f"{GITHUB_API_URL}/pulls"
    
    payload = {
        "title": title,
        "body": body,
        "head": head_branch,
        "base": BASE_BRANCH
    }
    
    print(f"-> Creating Pull Request from '{head_branch}' to '{BASE_BRANCH}'...")
    response = requests.post(pr_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 201: # 201 Created
        pr_data = response.json()
        print(f"   Success! Pull Request created.")
        print(f"   View it here: {pr_data['html_url']}")
        return True
    else:
        error_message = response.json().get('errors', [{}])[0].get('message', '')
        if "A pull request already exists" in error_message:
            print("   Info: Pull Request already exists for this branch.")
            return True
        print(f"!! Error creating pull request: {response.json()}")
        return False

# --- FINAL Local Testing Block ---
if __name__ == "__main__":
    pat = os.getenv('GITHUB_PAT')
    if not pat:
        print("\n!! ERROR: GITHUB_PAT environment variable not set.")
    else:
        # Define the fix
        package_to_fix = "tqdm"
        new_package_version = "4.66.1" # A real, recent version
        branch_name = f"agent-fix/upgrade-{package_to_fix}"
        
        # Define the PR details
        pr_title = f"CodeSentinel AI: Upgrade {package_to_fix}"
        pr_body = f"""
This is an automated pull request created by CodeSentinel AI.

**Vulnerability Detected:**
The version of `{package_to_fix}` in use has a low trust score.

**Proposed Fix:**
Upgrading `{package_to_fix}` to version `{new_package_version}`.

Please review and merge this change.
"""
        # Run the full agent sequence
        if create_new_branch(branch_name, pat):
            if update_requirements_file(branch_name, package_to_fix, new_package_version, pat):
                create_pull_request(branch_name, pr_title, pr_body, pat)