import os
import json
import argparse
from datetime import datetime
from sonarqube import SonarQubeClient

sonar = SonarQubeClient(sonarqube_url="http://localhost:9000", token='005262c36323025d91963a83b684499a0f841808')

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Fetching and Saving SonarQube Issues')
parser.add_argument('--date', type=str, help='Specify the date to replace in the file name')
args = parser.parse_args()

# Load the filtered repositories JSON file
date_argument = args.date if args.date else datetime.now().strftime('%d-%m-%Y')
file_name = f'filtered-repositories-{date_argument}.json'

with open(file_name, 'r') as file:
    filtered_data = json.load(file)
    repositories = filtered_data.get('repositories')

fetched_issues_data = {}

for repo in repositories:
    sonarProjectKey = repo.get('SonarProjectKey')
    print(f"Fetching issues for project key: {sonarProjectKey}")

    page = 1
    has_more_issues = True
    fetched_issues = 0
    issues_data = []  # Store issues data for the current project

    while has_more_issues:
        issues = sonar.issues.search_issues(
            componentKeys=sonarProjectKey, 
            type="CODE_SMELL",
            ps="100",  # Set the page size to 100 (adjust as needed)
            p=str(page)  # Set the current page number
        )

        project_issues = issues.get('issues', [])
        if not project_issues:
            break  # Exit loop if no more issues for the project or all issues fetched

        issues_data.extend(project_issues)

        total_issues = issues.get('paging', {}).get('total', 0)
        fetched_issues = len(issues.get('issues', [])) * page

        print(f"Issues fetched: {fetched_issues} / Total issues: {total_issues}")

        if fetched_issues >= total_issues:
            has_more_issues = False
        else:
            page += 1

    fetched_issues_data[sonarProjectKey] = issues_data  # Map project key to its fetched issues

# Save the fetched issues data to a JSON file
output_file = 'fetched_issues_data.json'
with open(output_file, 'w') as json_file:
    json.dump(fetched_issues_data, json_file, indent=4)

print(f"Data saved to {output_file}")
