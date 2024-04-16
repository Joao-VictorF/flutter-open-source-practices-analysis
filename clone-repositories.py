import json
import os
import argparse
from datetime import datetime

# Function to clone GitHub repositories
def clone_repositories(filtered_data, clone_directory):
    for repo in filtered_data['repositories']:
        clone_url = repo.get('Clone URL')
        if clone_url:
            repository_name = clone_url.split('/')[-1][:-4]  # Extract repository name from the URL
            clone_path = os.path.join(clone_directory, repository_name)
            os.system(f'git clone {clone_url} {clone_path}')
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
