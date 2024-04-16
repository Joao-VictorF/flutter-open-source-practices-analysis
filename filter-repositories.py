import os
import json
from dotenv import load_dotenv 
from datetime import datetime
from tabulate import tabulate

load_dotenv() 

# Load the JSON data from the file
with open('repositories_data.json', 'r') as file:
    data = json.load(file)

# Define the environment variables for filtering
MIN_STARS = int(os.getenv("MIN_STARS"))
MIN_FORKS = int(os.getenv("MIN_FORKS"))
MIN_COMMITS = int(os.getenv("MIN_COMMITS"))
MIN_WATCHERS = int(os.getenv("MIN_WATCHERS"))
MIN_OPEN_ISSUES = int(os.getenv("MIN_OPEN_ISSUES"))
MIN_CONTRIBUTORS = int(os.getenv("MIN_CONTRIBUTORS"))
MAX_LAST_COMMIT_YEARS = int(os.getenv("MAX_LAST_COMMIT_YEARS"))

filtered_repositories = [repo for repo in data.values() if 
                         datetime.strptime(repo['Last Commit'], '%d/%m/%Y').year >= MAX_LAST_COMMIT_YEARS
                         and repo['Stars'] >= MIN_STARS
                         and repo['Watchers'] >= MIN_WATCHERS
                         and repo['Commits'] >= MIN_COMMITS
                         and repo['Contributors'] >= MIN_CONTRIBUTORS
                         and repo['Forks'] >= MIN_FORKS
                         and repo['Issues (Open)'] >= MIN_OPEN_ISSUES]

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
output_filename = f'filtered-repositories-{current_date}.json'

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
