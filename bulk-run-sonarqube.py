import os
import json
import argparse
from datetime import datetime

# Function to run commands inside each repository
def runSonarQube(repositories, clone_directory):
    original_directory = os.getcwd()  # Save the original working directory

    for repo in repositories:
        if repo.get('SonarQubeExecuted') == True:
            continue

        if input(f"Do you want to run commands in the next project '{repo.get('Name')}'? (y/n): ").lower() != 'y':
            print("Exiting the script.")
            break

        repository_name = repo.get('Name')
        repository_path = os.path.join(clone_directory, repository_name)

        # Move to the repository directory
        os.chdir(repository_path)
        print(f"Entered directory: {repository_name}")

        # Run commands inside the repository
        print(f"Running commands inside {repository_name}...")
        os.system("flutter pub get")
        print(f"Ran 'flutter pub get' in {repository_name}")

        os.system("flutter test --machine --coverage")
        print(f"Ran 'flutter test --machine --coverage' in {repository_name}")

        os.system("sonar-scanner")
        print(f"Ran 'sonar-scanner' in {repository_name}")

        # Return to the original directory after processing a repository
        os.chdir(original_directory)  # Return to the original directory

# Specify the directory where the repositories are cloned
clone_directory = '../cloned-projects'

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Clone GitHub repositories')
parser.add_argument('--date', type=str, help='Specify the date to replace in the file name')
args = parser.parse_args()

# Load the filtered repositories JSON file
date_argument = args.date if args.date else datetime.now().strftime('%d-%m-%Y')
file_path = f'json-files/filtered-repositories-{date_argument}.json'

with open(file_path, 'r') as file:
    filtered_data = json.load(file)
    repositories = filtered_data.get('repositories')

# Run commands inside each repository
runSonarQube(repositories, clone_directory)
