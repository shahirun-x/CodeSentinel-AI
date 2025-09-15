# main.py
import requests
import re
from datetime import datetime, timezone
import time
from colorama import Fore, Style, init
import re # Add this new import for pattern matching
import tarfile # For handling .tar.gz files
import io      # For handling in-memory files

TRUSTED_PACKAGES = {'pandas', 'numpy'}
# --- NO CHANGES TO THIS FUNCTION ---
def parse_requirements(filepath):
    packages = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            line = line.split('#')[0].strip()
            if not line: continue
            package_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
            packages.append(package_name)
    return packages

# --- NO CHANGES TO THIS FUNCTION ---
def get_package_data(package_name):
    print(f"-> Gathering intelligence for '{package_name}'...")
    api_url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"   [Error] Could not find package: {package_name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"   [Error] Network error: {e}")
        return None

# --- NEW HELPER FUNCTION 1 ---
def extract_github_username(pypi_data):
    """Searches project URLs to find a GitHub username."""
    info = pypi_data.get('info', {})
    urls_to_check = [info.get('home_page', '')]
    project_urls = info.get('project_urls', {})
    if project_urls:
        urls_to_check.extend(project_urls.values())

    for url in urls_to_check:
        if url and 'github.com' in url:
            # Use a regular expression to find 'github.com/username'
            match = re.search(r"github\.com/([^/]+)", url)
            if match:
                return match.group(1)
    return None

# --- NEW HELPER FUNCTION 2 ---
def get_github_user_info(username):
    """Fetches user or organization data from the GitHub API."""
    print(f"   -> Running background check on GitHub user: '{username}'...")
    api_url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None
    
 #--- NEW FUNCTION: The Source Code Scanner ---

# In main.py, replace this function

def analyze_source_code(package_name, version):
    """
    Downloads, decompresses, and scans package source code for dangerous patterns.
    """
    print(f"   -> Performing static code analysis for '{package_name}'...")
    package_info = get_package_data(package_name)
    if not package_info or not package_info.get('releases', {}).get(version):
        return []

    source_url = None
    for file_info in package_info['releases'][version]:
        if file_info['packagetype'] == 'sdist':
            source_url = file_info['url']
            break
    
    if not source_url:
        return ["Could not find source code distribution (.tar.gz) to scan."]

    try:
        response = requests.get(source_url, stream=True)
        response.raise_for_status()
        
        tar_file_object = io.BytesIO(response.content)
        tar = tarfile.open(fileobj=tar_file_object, mode="r:gz")
        
        dangerous_patterns = {
            "os.system": "High-risk OS command execution",
            "subprocess.run": "Potential for arbitrary command execution",
            "eval(": "Execution of arbitrary strings as code",
            "exec(": "Execution of arbitrary strings as code",
            "pickle.load": "Potential for arbitrary code execution during deserialization"
        }
        findings = []

        for member in tar.getmembers():
            # --- THIS IS THE ONLY CHANGE ---
            # We add a check to ignore files in any 'tests' directory.
            if member.isfile() and member.name.endswith('.py') and '/tests/' not in member.name:
                file_content = tar.extractfile(member).read().decode('utf-8', errors='ignore')
                for line_num, line in enumerate(file_content.splitlines(), 1):
                    for pattern, description in dangerous_patterns.items():
                        if pattern in line:
                            finding = f"'{pattern}' found in '{member.name}' (line {line_num}) - {description}."
                            findings.append(finding)
        return findings

    except Exception as e:
        return [f"Failed to analyze source code: {e}"]
    
# In main.py, replace the whole function

def calculate_trust_score(package_data, version):
    score = 100
    risk_factors = []
    info = package_data.get('info', {})
    package_name = info.get('name', '')
    releases = package_data.get('releases', {})

    # ... (Rules 1-6 are the same as before) ...
    if not info.get('author'): score -= 5; risk_factors.append("Missing author name in PyPI metadata.")
    if not info.get('home_page'): score -= 10; risk_factors.append("No project homepage listed.")
    if releases:
        all_upload_times = []
        for version_files in releases.values():
            for file_info in version_files:
                upload_time_str = file_info.get('upload_time_iso_8601')
                if upload_time_str: all_upload_times.append(datetime.fromisoformat(upload_time_str))
        if all_upload_times:
            first_release_date = min(all_upload_times)
            days_since_first_release = (datetime.now(timezone.utc) - first_release_date).days
            if days_since_first_release < 180: score -= 20; risk_factors.append(f"Package is new (created {days_since_first_release} days ago).")
    else: score -= 10; risk_factors.append("No release history found.")
    if len(releases) <= 2: score -= 5; risk_factors.append("Very few versions published.")
    github_username = extract_github_username(package_data)
    if github_username:
        github_info = get_github_user_info(github_username)
        if github_info:
            followers = github_info.get('followers', 0)
            if followers < 20: score -= 15; risk_factors.append(f"GitHub account ({github_username}) has few followers ({followers}).")
            created_at_str = github_info.get('created_at')
            created_at_date = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            days_since_creation = (datetime.now(timezone.utc) - created_at_date).days
            if days_since_creation < 365: score -= 20; risk_factors.append(f"GitHub account ({github_username}) is new ({days_since_creation} days old).")
        else: score -= 10; risk_factors.append(f"Could not verify GitHub username: {github_username}.")
    else: score -= 15; risk_factors.append("No associated GitHub repository found.")

    # --- FINAL REFINED RULE 8: CONTEXT-AWARE STATIC CODE ANALYSIS ---
    code_findings = analyze_source_code(package_name, version)
    if code_findings:
        if package_name in TRUSTED_PACKAGES:
            # It's a trusted package, so this is a low-risk note, not a critical failure.
            score -= 5 
            risk_factors.append(f"[Note] Potentially risky code patterns found, but this is a trusted package.")
        else:
            # It's an unknown package, so this is a major red flag.
            score -= 60
            risk_factors.extend(code_findings)

    return max(0, score), risk_factors

# --- NO CHANGES TO THIS FUNCTION ---
def display_report(results):
    init(autoreset=True)
    print("\n--- CodeSentinel AI: Final Report ---")
    results.sort(key=lambda x: x['score'])
    for result in results:
        score = result['score']
        name = result['name']
        factors = result['factors']
        color = Fore.GREEN
        if score < 50: color = Fore.RED
        elif score < 80: color = Fore.YELLOW
        print(f"\nPackage: {Style.BRIGHT}{name}")
        print(f"  Trust Score: {color}{Style.BRIGHT}{score}/100")
        if factors:
            print(f"  {Fore.RED}Identified Risk Factors:")
            for factor in factors:
                print(f"    - {factor}")
        else:
            print(f"  {Fore.GREEN}No major risk factors identified.")
    print("\n--- End of Report ---")

# --- NO CHANGES TO THIS BLOCK ---
if __name__ == "__main__":
    print("--- CodeSentinel AI: Starting Full Analysis ---")
    filepath = 'requirements.txt'
    dependencies = parse_requirements(filepath)
    print(f"Found {len(dependencies)} packages to analyze...")
    analysis_results = []
    for package in dependencies:
        data = get_package_data(package)
        if data:
            score, factors = calculate_trust_score(data)
            result = {"name": package, "score": score, "factors": factors}
            analysis_results.append(result)
        time.sleep(0.5)
    display_report(analysis_results)