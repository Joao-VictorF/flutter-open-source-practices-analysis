import pandas as pd
import json
import matplotlib.pyplot as plt

# Load the JSON data containing the project issues
with open('json-files/fetched_issues_data.json') as file:
    data = json.load(file)

# Create a DataFrame from the JSON data
df = pd.DataFrame(data['4seer/openflutterecommerceapp']['issues'])

# Update column titles for better readability
df.columns = [
    'Issue Key', 'Rule', 'Severity', 'Component', 'Project', 'Hash', 'Text Range',
    'Flows', 'Resolution', 'Status', 'Message', 'Effort', 'Debt', 'Author',
    'Tags', 'Creation Date', 'Update Date', 'Close Date', 'Issue Type', 'Scope', 'Line'
]

# Display null value counts for each column
print("Null Value Counts:")
print(df.isnull().sum())

# Improve data type information display
print("Data Types Information:")
print(df.dtypes)

# Display the first few rows of the DataFrame with updated column titles
print("Sample Data:")
print(df.head())

# Summary statistics and information about the DataFrame
print("Data Description:")
print(df.describe())
print("Data Information:")
print(df.info())

# Create charts to visualize severity distribution
# Count the frequency of each severity level
severity_counts = df['Severity'].value_counts()

plt.figure(figsize=(14, 6))

# Create a bar chart to visualize severity distribution
plt.subplot(1, 2, 1)
severity_counts.plot(kind='bar', color='skyblue')
plt.title('Distribution of Severity Levels in Project Issues')
plt.xlabel('Severity Levels')
plt.ylabel('Count')
plt.xticks(rotation=0)  # Rotate x-axis labels if needed

# Create a pie chart to visualize the proportion of severity levels
plt.subplot(1, 2, 2)
plt.pie(severity_counts, labels=severity_counts.index, autopct='%1.1f%%', startangle=140, colors=['lightcoral', 'lightskyblue', 'lightgreen'])
plt.title('Proportion of Severity Levels in Project Issues')

plt.tight_layout()  # Adjust subplots to prevent overlap
plt.show()
