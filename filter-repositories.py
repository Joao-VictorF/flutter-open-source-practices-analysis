import os
import json
from dotenv import load_dotenv 
from datetime import datetime
from tabulate import tabulate

load_dotenv() 

# Load the JSON data from the file
with open('json-files/repositories_data.json', 'r') as file:
    data = json.load(file)

# Define the environment variables for filtering
MIN_STARS = int(os.getenv("MIN_STARS"))
MIN_FORKS = int(os.getenv("MIN_FORKS"))
MIN_COMMITS = int(os.getenv("MIN_COMMITS"))
MIN_WATCHERS = int(os.getenv("MIN_WATCHERS"))
MIN_OPEN_ISSUES = int(os.getenv("MIN_OPEN_ISSUES"))
MIN_CONTRIBUTORS = int(os.getenv("MIN_CONTRIBUTORS"))
MAX_LAST_COMMIT_YEARS = int(os.getenv("MAX_LAST_COMMIT_YEARS"))

filtered_repositories = []
current_year = datetime.now().year

for repo_data in data.values():
    last_commit_date = datetime.strptime(repo_data['Last Commit'], '%d/%m/%Y')
    years_since_last_commit = current_year - last_commit_date.year

    is_recent_commit = years_since_last_commit <= MAX_LAST_COMMIT_YEARS
    meets_stars_criteria = repo_data['Stars'] >= MIN_STARS
    meets_watchers_criteria = repo_data['Watchers'] >= MIN_WATCHERS
    meets_commits_criteria = repo_data['Commits'] >= MIN_COMMITS
    meets_contributors_criteria = repo_data['Contributors'] >= MIN_CONTRIBUTORS
    meets_forks_criteria = repo_data['Forks'] >= MIN_FORKS
    has_open_issues_criteria = repo_data['Issues (Open)'] >= MIN_OPEN_ISSUES

    if is_recent_commit and meets_stars_criteria and meets_watchers_criteria \
            and meets_commits_criteria and meets_contributors_criteria \
            and meets_forks_criteria and has_open_issues_criteria:
        filtered_repositories.append(repo_data)

# Create the filtered data structure
filtered_data = {
    'totalRepositories': len(filtered_repositories),
    'settings': {
        'MIN_STARS': MIN_STARS,
        'MIN_FORKS': MIN_FORKS,
        'MIN_COMMITS': MIN_COMMITS,
        'MIN_WATCHERS': MIN_WATCHERS,
        'MIN_OPEN_ISSUES': MIN_OPEN_ISSUES,
        'MIN_CONTRIBUTORS': MIN_CONTRIBUTORS,
        'MAX_LAST_COMMIT_YEARS': MAX_LAST_COMMIT_YEARS,
    },
    'repositories': filtered_repositories
}

current_date = datetime.now().strftime('%d-%m-%Y')
output_filename = f'json-files/filtered-repositories-{current_date}.json'

# Save the filtered data to a new JSON file
with open(output_filename, 'w') as outfile:
    json.dump(filtered_data, outfile, indent=4)

# Print the settings in a tabular format
settings_table = [["Setting", "Value"]]
for key, value in filtered_data['settings'].items():
    settings_table.append([key, value])

print(tabulate(settings_table, headers="firstrow", tablefmt="grid"))
print("\n\nTotal filtered repositories:", filtered_data['totalRepositories'])
print("\nSaved to:", output_filename)
