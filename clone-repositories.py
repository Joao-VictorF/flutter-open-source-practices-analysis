import os
import json
import argparse
from datetime import datetime

# Create the sonar-project.properties file
def createSonarPropertiesFile(clone_path, repository_name, sonarProjectKey):
    properties_content = f"""
    sonar.projectKey={sonarProjectKey}
    sonar.projectName={repository_name}
    sonar.login=005262c36323025d91963a83b684499a0f841808

    sonar.host.url=http://localhost:9000

    # Source code location.
    # Path is relative to the sonar-project.properties file. Defaults to .
    # Use commas to specify more than one folder.
    sonar.sources=lib
    sonar.tests=test

    # Encoding of the source code. Default is default system encoding.
    sonar.sourceEncoding=UTF-8

    # exclude generated files
    sonar.exclusions=test/**/*_test.mocks.dart,lib/**/*.g.dart
    """

    with open(os.path.join(clone_path, "sonar-project.properties"), 'w') as file:
        file.write(properties_content)

# Function to clone GitHub repositories
def clone_repositories(filtered_data, clone_directory):
    for repo in filtered_data['repositories']:
        clone_url = repo.get('Clone URL')
        projectKey = repo.get('SonarProjectKey')

        if clone_url:
            repository_name = clone_url.split('/')[-1][:-4]  # Extract repository name from the URL
            clone_path = os.path.join(clone_directory, repository_name)
            os.system(f'git clone {clone_url} {clone_path}')
            createSonarPropertiesFile(clone_path, repository_name, projectKey)
            
            print(f"Cloned repository {repository_name} to {clone_path}")

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Clone GitHub repositories')
parser.add_argument('--date', type=str, help='Specify the date to replace in file name')
args = parser.parse_args()

# Load the filtered repositories JSON file
date_argument = args.date if args.date else datetime.now().strftime('%d-%m-%Y')
file_name = f'filtered-repositories-{date_argument}.json'

with open(file_name, 'r') as file:
    filtered_data = json.load(file)

# Specify the directory where you want to clone the repositories
clone_directory = '../cloned-projects'

# Create the clone directory if it doesn't exist
os.makedirs(clone_directory, exist_ok=True)

# Clone the repositories
clone_repositories(filtered_data, clone_directory)
