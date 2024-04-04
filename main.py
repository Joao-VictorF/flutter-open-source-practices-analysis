import os
import json
import requests
import openpyxl

from dotenv import load_dotenv 
from datetime import datetime
from tabulate import tabulate

load_dotenv() 

def fetch_repository_info(repo_url, repo_type):
    owner, repo_name = repo_url.split('/')[-2:]
    token = os.getenv("GITHUB_TOKEN")
    headers = { "Authorization": f"Bearer {token}" }

    repository_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=1&page=1"

    repo_response = requests.get(repository_url, headers=headers)
    commits_response = requests.get(commits_url, headers=headers)

    if repo_response.status_code == 200 and commits_response.status_code == 200:
        repo_info = repo_response.json()
        link_header = commits_response.headers.get('Link')
        total_commits = int(link_header.split(';')[1].split('&page=')[-1].split('>')[0])

        last_commit_date = None
        if total_commits > 0:
            last_commit_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=1"
            last_commit_response = requests.get(last_commit_url, headers=headers)

            if last_commit_response.status_code != 200:
                return None

            last_commit_info = last_commit_response.json()
            last_commit_date = last_commit_info[0]['commit']['author']['date']
            last_commit_date = datetime.strptime(last_commit_date, "%Y-%m-%dT%H:%M:%SZ")
            last_commit_date = last_commit_date.strftime("%d/%m/%Y")
        
        contributors_url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
        contributors_response = requests.get(contributors_url, headers=headers)

        if contributors_response.status_code != 200:
            return None

        contributors_count = len(contributors_response.json())

        return {
            'Consult Date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'Last Commit': last_commit_date,
            'Name': repo_info['name'],
            'Category': repo_type,
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

def verifySpreadsheet():
    file_path = 'repositories_data.xlsx'
    if not os.path.exists(file_path):
        wb = openpyxl.Workbook()
        wb.save(file_path)
def main():
    with open('repositories.json') as f:
        repos = json.load(f)

    # Load Excel workbook
    verifySpreadsheet()
    wb = openpyxl.load_workbook('repositories_data.xlsx')
    ws = wb.active

    table_data = []
    for i, repo in enumerate(repos, start=1):
        if repo.get('read'):
            continue  # Skip if repository has already been read
        
        repo_info = fetch_repository_info(repo['url'], repo['type'])

        if repo_info == None:
            print('Exiting the app as the repo_info is None')
            break

        if repo_info:
            # Append repository info to Excel file
            row = [
                repo_info['Consult Date'],
                repo_info['Last Commit'],
                repo_info['Name'],
                repo_info['Category'],
                repo_info['Stars'],
                repo_info['Watchers'],
                repo_info['Commits'],
                repo_info['Contributors'],
                repo_info['Forks'],
                repo_info['Issues (Open)'],
                repo_info['Clone URL'],
                repo_info['SonarProjectKey']
            ]
            ws.append(row)
            wb.save('repositories_data.xlsx')

            # Append repository info to table_data for tabulation
            table_data.append(row)

            repo['read'] = True
            # Print progress
            print(f"Reading repository {i}/{len(repos)}: {repo_info['Name']}")

    with open('repositories.json', 'w') as json_file:
        json.dump(repos, json_file, indent=2)
    
    headers = [
        'Consult Date',
        'Last Commit',
        'Name',
        'Category',
        'Stars',
        'Watchers',
        'Commits',
        'Contributors',
        'Forks',
        'Issues (Open)',
        'Clone URL',
        'SonarProjectKey'
    ]
    print(tabulate(table_data, headers=headers, tablefmt="grid", stralign="left"))

    with open('repositories_data.json', 'r') as f:
        existing_data = json.load(f)

    json_data = []
    for row in table_data:
        json_data.append(dict(zip(headers, row)))

    for item in json_data:
        existing_data[item['SonarProjectKey']] = item

    with open('repositories_data.json', 'w') as f:
     json.dump(existing_data, f, indent=2)


if __name__ == "__main__":
    main()
