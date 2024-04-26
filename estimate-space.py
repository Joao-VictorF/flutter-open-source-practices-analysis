import os
import json
import requests
import argparse
from dotenv import load_dotenv 

load_dotenv()

# Fetch the size of a GitHub repository from the GitHub API
def get_repository_size(sonarProjectKey):
    token = os.getenv("GITHUB_TOKEN")
    [owner, repo_name] = sonarProjectKey.split(':')

    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = { "Authorization": f"Bearer {token}" }
    response = requests.get(api_url, headers=headers)


    if response.status_code == 200:
        repo_data = response.json()
        total_size_kb = repo_data.get('size', 0)
        total_size_mb = total_size_kb / 1024  # Convert KB to MB
        total_size_gb = total_size_mb / 1024  # Convert MB to GB
        print(f'{sonarProjectKey}: {"{:.1f}".format(total_size_mb)}MB')

        return total_size_gb
    return 0

# Function to estimate the total space required for cloning in MB
def estimate_space(filtered_data):
    total_size_gb = 0
    for repo in filtered_data['repositories']:
        sonarProjectKey = repo.get('SonarProjectKey')
        repo_size = get_repository_size(sonarProjectKey)
        total_size_gb += repo_size

    return total_size_gb

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Estimate space occupied by GitHub repositories')
parser.add_argument('--date', type=str, help='Specify the date to replace in file name')
args = parser.parse_args()

# Load the filtered repositories JSON file
date_argument = args.date if args.date else datetime.now().strftime('%d-%m-%Y')
file_name = f'filtered-repositories-{date_argument}.json'

with open(file_name, 'r') as file:
    filtered_data = json.load(file)

estimated_size = estimate_space(filtered_data)
print(f"Estimated total space required for cloning: {estimated_size:.2f} GB")
