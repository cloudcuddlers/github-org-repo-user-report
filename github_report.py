import requests
import csv
import os
import argparse
from typing import Dict, List, Any
import time


def get_headers(token: str) -> Dict[str, str]:
    """Return headers for GitHub API requests including authentication."""
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }


def get_organizations(token: str) -> List[Dict[str, Any]]:
    """Get list of organizations that the authenticated user belongs to."""
    headers = get_headers(token)
    response = requests.get('https://api.github.com/user/orgs', headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching organizations: {response.status_code}")
        print(response.json())
        return []
    
    return response.json()


def get_repos_for_org(org_name: str, token: str) -> List[Dict[str, Any]]:
    """Get all repositories for a given organization."""
    headers = get_headers(token)
    all_repos = []
    page = 1
    
    while True:
        response = requests.get(
            f'https://api.github.com/orgs/{org_name}/repos',
            headers=headers,
            params={'per_page': 100, 'page': page}
        )
        
        if response.status_code != 200:
            print(f"Error fetching repositories for {org_name}: {response.status_code}")
            print(response.json())
            return all_repos
        
        repos = response.json()
        if not repos:
            break
            
        all_repos.extend(repos)
        page += 1
        
        # Respect GitHub API rate limits
        if 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) < 10:
            print("Rate limit approaching, sleeping for a minute...")
            time.sleep(60)
    
    return all_repos


def get_collaborators_for_repo(org_name: str, repo_name: str, token: str) -> List[Dict[str, Any]]:
    """Get all collaborators with their permissions for a repository."""
    headers = get_headers(token)
    all_collaborators = []
    page = 1
    
    while True:
        response = requests.get(
            f'https://api.github.com/repos/{org_name}/{repo_name}/collaborators',
            headers=headers,
            params={'per_page': 100, 'page': page, 'affiliation': 'all'}
        )
        
        if response.status_code != 200:
            print(f"Error fetching collaborators for {org_name}/{repo_name}: {response.status_code}")
            print(response.json())
            return all_collaborators
        
        collaborators = response.json()
        if not collaborators:
            break
            
        all_collaborators.extend(collaborators)
        page += 1
        
        # Respect GitHub API rate limits
        if 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) < 10:
            print("Rate limit approaching, sleeping for a minute...")
            time.sleep(60)
    
    return all_collaborators


def get_user_email(username: str, token: str) -> str:
    """Try to get user's email address if publicly available."""
    headers = get_headers(token)
    response = requests.get(f'https://api.github.com/users/{username}', headers=headers)
    
    if response.status_code != 200:
        return "Not available"
    
    user_data = response.json()
    email = user_data.get('email')
    
    if not email:
        # Try to get email from user's events if not directly available
        events_response = requests.get(
            f'https://api.github.com/users/{username}/events/public',
            headers=headers
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            for event in events:
                if event['type'] == 'PushEvent' and 'payload' in event:
                    commits = event['payload'].get('commits', [])
                    for commit in commits:
                        if 'author' in commit and commit['author'].get('email'):
                            email = commit['author']['email']
                            if not email.endswith('noreply.github.com'):
                                return email
    
    return email if email else "Not available"


def get_permission_level(permissions: Dict[str, bool]) -> str:
    """Determine permission level based on permission flags."""
    if permissions.get('admin', False):
        return 'Admin'
    elif permissions.get('maintain', False):
        return 'Maintain'
    elif permissions.get('push', False):
        return 'Write'
    elif permissions.get('triage', False):
        return 'Triage'
    elif permissions.get('pull', False):
        return 'Read'
    else:
        return 'Unknown'


def generate_report(org_names: List[str], output_file: str, token: str) -> None:
    """Generate CSV report for specified GitHub organizations."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Organization', 'Repo Name', 'User Name', 'Email', 'Permission'])
        
        # If no specific organizations provided, get all organizations for the user
        if not org_names:
            orgs = get_organizations(token)
            org_names = [org['login'] for org in orgs]
            print(f"Found {len(org_names)} organizations: {', '.join(org_names)}")
        
        for org_name in org_names:
            print(f"Processing organization: {org_name}")
            repos = get_repos_for_org(org_name, token)
            print(f"Found {len(repos)} repositories in {org_name}")
            
            for repo in repos:
                repo_name = repo['name']
                print(f"  Processing repository: {repo_name}")
                collaborators = get_collaborators_for_repo(org_name, repo_name, token)
                
                for collaborator in collaborators:
                    username = collaborator['login']
                    email = get_user_email(username, token)
                    permission = get_permission_level(collaborator['permissions'])
                    
                    csv_writer.writerow([org_name, repo_name, username, email, permission])
                    
                print(f"  Added {len(collaborators)} collaborators for {repo_name}")
    
    print(f"Report generated successfully: {output_file}")


def main():
    """Main function to parse arguments and execute the report generation."""
    parser = argparse.ArgumentParser(description='Generate a CSV report of GitHub organization repositories and users')
    parser.add_argument('-t', '--token', help='GitHub Personal Access Token')
    parser.add_argument('-o', '--output', default='github_org_report.csv', help='Output CSV file name')
    parser.add_argument('-org', '--organizations', nargs='+', help='Specific GitHub organizations to include (space-separated)')
    
    args = parser.parse_args()
    
    # Get token from argument or environment variable
    token = args.token or os.environ.get('GITHUB_TOKEN')
    if not token:
        token = input("Please enter your GitHub Personal Access Token: ")
    
    generate_report(args.organizations, args.output, token)


if __name__ == "__main__":
    main()
