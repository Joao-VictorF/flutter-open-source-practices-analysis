import os
import json
import argparse
from datetime import datetime
from sonarqube import SonarQubeClient
import requests
import urllib.parse

FETCH_SOURCE_LINES = False
# Function to fetch the source lines for a component with pagination using recursion
def fetch_source_lines(component_key, initial_line=1, batch_size=500, source_code=[]):
    encoded_component_key = urllib.parse.quote(component_key, safe='')
    url = f"http://localhost:9000/api/sources/lines?from={initial_line}&to={initial_line + batch_size - 1}&key={encoded_component_key}"
    headers = { "Authorization": "Basic MDA1MjYyYzM2MzIzMDI1ZDkxOTYzYTgzYjY4NDQ5OWEwZjg0MTgwODo=" }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        current_source_lines = data.get('sources', [])
        
        if current_source_lines: 
            source_code.extend(current_source_lines)
            return fetch_source_lines(component_key, initial_line + batch_size, batch_size, source_code)
        else:
            return source_code
    else:
        return None

# Extract simplified sources schema with Array of "code" attributes
def simplify_sources_schema(project_data):
    for project_key, data in project_data.items():
        sources = data.get("sources", {})
        for component, code_lines in sources.items():
            simplified_code = [line.get("code", "") for line in code_lines]
            project_data[project_key]["sources"][component] = simplified_code
    return project_data

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

# Function to fetch and process data in the desired order for a project
def fetch_and_process_data(sonar, project_key):
    # Fetch issues for the project
    issues_data, _ = fetch_project_issues(sonar, project_key)

    # Process issues to extract unique components
    unique_components = set(issue.get("component") for issue in issues_data if issue.get("component"))
    unique_components_list = list(unique_components)

    # Initialize the project dictionary with issues and components
    project_data = {
        "issues": issues_data,
        "components": unique_components_list,
        "sources": {}  # Placeholder for source data
    }

    # Fetch source lines for each component in the project
    if FETCH_SOURCE_LINES:
        for component in project_data["components"]:
            source_lines = fetch_source_lines(component)
            if source_lines:
                project_data["sources"][component] = source_lines

    return project_data

# Main function to fetch and process data for a single project
def fetch_and_process_for_project(mocked_repositories, sonar):
    fetched_issues_data = {}

    for repo in mocked_repositories:
        sonarProjectKey = repo.get('SonarProjectKey')
        print(f"Processing data for project key: {sonarProjectKey}")

        # Fetch and process data sequentially for the selected project
        project_data = fetch_and_process_data(sonar, sonarProjectKey)
        fetched_issues_data[sonarProjectKey] = project_data
    
    # Simplify the sources schema before saving to JSON
    fetched_issues_data = simplify_sources_schema(fetched_issues_data)

    return fetched_issues_data

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Fetching and Saving SonarQube Issues')
parser.add_argument('--date', type=str, help='Specify the date to replace in the file name')
args = parser.parse_args()

date_argument = args.date if args.date else datetime.now().strftime('%d-%m-%Y')
file_name = f'json-files/filtered-repositories-{date_argument}.json'

# Initialize SonarQube client and fetch/process data for a single project
sonar = SonarQubeClient(sonarqube_url="http://localhost:9000", token='005262c36323025d91963a83b684499a0f841808')
with open(file_name, 'r') as file:
    filtered_data = json.load(file)
    repositories = filtered_data.get('repositories')

# Mocked list with a single project for testing
mocked_repositories = [repositories[0]]

# Fetch and process data for the mocked project
fetched_data = fetch_and_process_for_project(mocked_repositories, sonar)

# Save the fetched data to a JSON file
output_file = 'json-files/fetched_issues_data.json'
with open(output_file, 'w') as json_file:
    json.dump(fetched_data, json_file, indent=4)

print(f"Data saved to {output_file}")
