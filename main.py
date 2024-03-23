import json
import requests
from datetime import datetime
from tabulate import tabulate

def fetch_repository_info(repo_url):
    owner, repo_name = repo_url.split('/')[-2:]
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=1&page=1"
    
    response = requests.get(api_url)
    commits_response = requests.get(commits_url)

    if response.status_code == 200 and commits_response.status_code == 200:
        repo_info = response.json()
        link_header = commits_response.headers.get('Link')
        total_commits = int(link_header.split(';')[1].split('&page=')[-1].split('>')[0])

        last_commit_date = None
        last_commit_page = total_commits
        if total_commits > 0:
            last_commit_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=1&page={last_commit_page}"
            last_commit_response = requests.get(last_commit_url)
            last_commit_info = last_commit_response.json()
            last_commit_date = last_commit_info[0]['commit']['author']['date']
            last_commit_date = datetime.strptime(last_commit_date, "%Y-%m-%dT%H:%M:%SZ")
            last_commit_date = last_commit_date.strftime("%d/%m/%Y")
        
        contributors_url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
        contributors_response = requests.get(contributors_url)
        contributors_count = len(contributors_response.json())

        return {
            'Last Commit': last_commit_date,
            'Name': repo_info['name'],
            'Stars': repo_info['stargazers_count'],
            'Watchers': repo_info['subscribers_count'],
            'Commits': total_commits,
            'Contributors': contributors_count,
            'Forks': repo_info['forks_count'],
            'Issues (Open)': repo_info['open_issues'],
            'Clone URL': repo_info['clone_url'],
            'SonarProjectKey': repo_info['full_name'],
        }
    else:
        return None

def main():
    with open('repositories.json') as f:
        repo_urls = json.load(f)
    
    # table_data = []
    # for repo_url in repo_urls:
    #     repo_info = fetch_repository_info(repo_url)
    #     if repo_info:
    #         table_data.append(list(repo_info.values()))

    # headers = list(repo_info.keys()) if repo_info else []    
    # print(tabulate(table_data, headers=headers, tablefmt="grid"))

    table_data = []
    for repo_url in repo_urls:
        repo_info = fetch_repository_info(repo_url)
        if repo_info:
            table_data.append([
                repo_info['Last Commit'],
                repo_info['Name'],
                repo_info['Stars'],
                repo_info['Watchers'],
                repo_info['Commits'],
                repo_info['Contributors'],
                repo_info['Forks'],
                repo_info['Clone URL']
            ])
    headers = list(repo_info.keys())
    print(tabulate(table_data, headers=headers, tablefmt="grid", stralign="left"))

if __name__ == "__main__":
    main()
