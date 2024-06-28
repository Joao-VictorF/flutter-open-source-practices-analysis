import os
import json
import argparse
from datetime import datetime
from sonarqube import SonarQubeClient
import requests
import urllib.parse

SONARQUBE_HOST = 'http://host.docker.internal:9000'

# Function to fetch issues data for a project key
def fetch_project_issues(sonar, project_key):
    page = 1
    key = project_key.replace('/', ':')
    issues_data = []  # Store issues data for the current project
    total_issues = 0  # Initialize total_issues with a default value
    has_more_issues = True

    print(f"Fetching issues for project key: {key}")

    while has_more_issues:
        issues = sonar.issues.search_issues(
            componentKeys=key, 
            types="CODE_SMELL",
            ps="100",
            p=str(page),
            resolved="false"
        )

        project_issues = issues.get('issues', [])
        if not project_issues:
            break

        issues_data.extend(project_issues)
        total_issues = issues.get('paging', {}).get('total', 0)
        issues_fetched = len(issues.get('issues', [])) * page
        print(f"Issues fetched: {issues_fetched} / Total issues: {total_issues}")

        if issues_fetched >= total_issues:
            has_more_issues = False
        else:
            page += 1

    return issues_data, total_issues

# Function to fetch general metrics for a project
def fetch_project_metrics(sonar, project_key):
    metrics = 'ncloc,complexity,code_smells,duplicated_lines_density,sqale_index,sqale_debt_ratio,comment_lines_density,reliability_rating,bugs,reliability_remediation_effort,security_rating,vulnerabilities,security_remediation_effort,security_hotspots,files,directories'
    key = project_key.replace('/', ':')
    component = sonar.measures.get_component_with_specified_measures(
        component=key,
        fields="metrics,periods",
        metricKeys=metrics
    )
    return component

# Function to fetch and process data in the desired order for a project
def fetch_and_process_data(sonar, project_key):
    # Fetch issues for the project
    issues_data, _ = fetch_project_issues(sonar, project_key)

    # Fetch metrics for the project
    metrics_data = fetch_project_metrics(sonar, project_key)

    # Process issues to extract unique components
    unique_components = set(issue.get("component") for issue in issues_data if issue.get("component"))
    unique_components_list = list(unique_components)

    # Initialize the project dictionary with issues, components, and metrics
    project_data = {
        "issues": issues_data,
        "components": unique_components_list,
        "metrics": metrics_data
    }

    return project_data

# Main function to fetch and process data for a single project
def fetch_and_process_for_project(repositories, sonar):
    fetched_issues_data = {}

    for repo in repositories:
        sonarProjectKey = repo.get('SonarProjectKey')
        print(f"Processing data for project key: {sonarProjectKey}")

        # Fetch and process data sequentially for the selected project
        project_data = fetch_and_process_data(sonar, sonarProjectKey)
        fetched_issues_data[sonarProjectKey] = project_data
    
    return fetched_issues_data

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Fetching and Saving SonarQube Issues')
parser.add_argument('--date', type=str, help='Specify the date to replace in the file name')
args = parser.parse_args()

date_argument = args.date if args.date else datetime.now().strftime('%d-%m-%Y')
file_name = f'json-files/filtered-repositories-{date_argument}.json'

# Initialize SonarQube client and fetch/process data for a single project
sonar = SonarQubeClient(sonarqube_url=SONARQUBE_HOST, token='005262c36323025d91963a83b684499a0f841808')
with open(file_name, 'r') as file:
    filtered_data = json.load(file)
    repositories = filtered_data.get('repositories')

# Fetch and process data for the mocked project
fetched_data = fetch_and_process_for_project(repositories, sonar)

# Save the fetched data to a JSON file
output_file = f'json-files/fetched_issues_data-{date_argument}.json'
with open(output_file, 'w') as json_file:
    json.dump(fetched_data, json_file, indent=4)

print(f"Data saved to {output_file}")
