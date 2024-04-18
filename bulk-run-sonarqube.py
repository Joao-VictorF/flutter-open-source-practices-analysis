import os
import json
import argparse
import subprocess
from datetime import datetime

# Function to run commands inside each repository
def runSonarQube(repositories, clone_directory):
    for repo in filtered_data['repositories']:
        repository_name = repo.get('Name')
        repository_path = os.path.join(clone_directory, repository_name)

        # Move to the repository directory
        os.chdir(repository_path)
        print(f"Entered directory: {repository_name}")

        # Run commands inside the repository
        print(f"Running commands inside {repository_name}...")
        process = subprocess.Popen(["flutter", "pub", "get"], stdout=subprocess.PIPE)
        process.wait()
        print(f"Ran 'flutter pub get' in {repository_name}")

        process = subprocess.Popen(["flutter", "test", "--machine", "--coverage"], stdout=subprocess.PIPE)
        process.wait()
        print(f"Ran 'flutter test --machine --coverage' in {repository_name}")

        process = subprocess.Popen(["sonar-scanner"], stdout=subprocess.PIPE)
        process.wait()
        print(f"Ran 'sonar-scanner' in {repository_name}")

# Specify the directory where the repositories are cloned
clone_directory = '../cloned-projects'

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Clone GitHub repositories')
parser.add_argument('--date', type=str, help='Specify the date to replace in file name')
args = parser.parse_args()

# Load the filtered repositories JSON file
date_argument = args.date if args.date else datetime.now().strftime('%d-%m-%Y')
file_name = f'filtered-repositories-{date_argument}.json'

with open(file_name, 'r') as file:
    filtered_data = json.load(file)

# Run commands inside each repository
runSonarQube(filtered_data, clone_directory)
