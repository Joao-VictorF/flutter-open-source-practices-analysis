import pandas as pd
import json
import matplotlib.pyplot as plt

# project_key = '4seer/openflutterecommerceapp'
project_key = 'invoiceninja/admin-portal'
severity_colors = ['mediumaquamarine', 'orangered', 'mediumpurple']
def load_data(file_path):
    with open(file_path) as file:
        data = json.load(file)
    return data

def preprocess_data(data):
    df = pd.DataFrame(data[project_key]['issues'])
    df.columns = ['Issue Key', 'Rule', 'Severity', 'Component', 'Project', 'Line', 'Hash', 'Text Range',
                  'Flows', 'Status', 'Message', 'Effort', 'Debt', 'Author',
                  'Tags', 'Creation Date', 'Update Date', 'Issue Type', 'Scope']

    # Filter 'Component' column based on the 'Project' attribute
    project_name = data[project_key]['issues'][0]['project']
    df['Component'] = df['Component'].apply(lambda x: x.replace(f"{project_name}:", "") if f"{project_name}:" in x else x)
    
    return df

def analyze_effort_debt(df):
    effort_debt_analysis = df.groupby('Severity')[['Effort', 'Debt']].sum()
    effort_debt_analysis['Effort'] = pd.to_numeric(effort_debt_analysis['Effort'], errors='coerce')
    effort_debt_analysis['Debt'] = pd.to_numeric(effort_debt_analysis['Debt'], errors='coerce')
    # effort_debt_analysis = effort_debt_analysis.dropna(subset=['Effort', 'Debt'])
    return effort_debt_analysis

def analyze_component_distribution(df):
    component_distribution = df['Component'].value_counts()
    return component_distribution

def create_bar_chart_severity(severity_counts):
    # Create a bar chart to visualize severity distribution
    plt.subplot(1,2,1)
    plt.bar(severity_counts.index, severity_counts, color=severity_colors)
    plt.title('Distribution of Severity Levels in Code Smells') # for f{} project')
    plt.xlabel('Severity Levels')
    plt.ylabel('Count')
    plt.xticks(rotation=0)
    
    # Add value labels inside the bars
    for i, count in enumerate(severity_counts):
        plt.text(i, count, count, ha='center', va='bottom')

def create_pie_chart_severity(severity_counts):
    # Create a pie chart to visualize the proportion of severity levels
    plt.subplot(1,2,2)
    plt.pie(severity_counts, labels=severity_counts.index, autopct='%1.1f%%', startangle=140, colors=severity_colors)
    plt.title('Proportion of Severity Levels in Code Smells') # for f{} project')

def severity_charts():
    plt.figure(figsize=(18, 12))
    create_bar_chart_severity(severity_counts)
    create_pie_chart_severity(severity_counts)
    plt.show()

def rules_and_effort_charts():
    plt.figure(figsize=(18, 12))
    effort_chart(effort_debt_analysis)
    rule_analysis_chart(rule_counts)
    plt.show()

def effort_chart(effort_debt_analysis):
    # Effort and Debt Analysis Bar Chart
    # plt.figure(figsize=(18, 12))
    plt.subplot(1,2,1)
    effort_debt_analysis.plot(kind='bar', ax=plt.gca(), color=['lightblue', 'lightcoral'])
    plt.title('Effort and Debt Analysis by Severity Level')
    plt.xlabel('Severity Levels')
    plt.ylabel('Effort/Debt')
    plt.xticks(rotation=0)
    plt.legend(["Effort", "Debt"])
    # plt.show()

def issues_by_component_chart(component_distribution):
    # Component Analysis Bar Chart
    plt.figure(figsize=(18, 12))

    component_distribution.plot(kind='bar', color='skyblue')
    plt.title('Issue Distribution by Component')
    plt.xlabel('Component')
    plt.ylabel('Issue Count')
    plt.xticks(rotation=90, ha='right')
    plt.show()

def rule_analysis_chart(rule_counts):
    plt.subplot(1,2,2)
    bar_plot = rule_counts.plot(kind='bar', color='skyblue')
    plt.title('Frequency of Issue Rules')
    plt.xlabel('Rule')
    plt.ylabel('Count')
    plt.xticks(rotation=90)
    
    # Add rule descriptions inside the bars
    for i, count in enumerate(rule_counts):
        rule = rule_counts.index[i]
        plt.text(i, count, f"{rule}\n{count}", ha='center', va='bottom', rotation=0, fontsize=8)
    
    plt.show()


def rule_analysis(df):
    df['Rule'] = df['Rule'].apply(lambda x: x.replace('dartanalyzer:', ''))
    rule_counts = df['Rule'].value_counts()
    return rule_counts

def visualize_data(severity_counts, effort_debt_analysis, component_distribution, rule_counts):
    severity_charts()
    rules_and_effort_charts()
    issues_by_component_chart(component_distribution)

if __name__ == "__main__":
    file_path = 'json-files/fetched_issues_data.json'
    
    # Load and preprocess the data
    data = load_data(file_path)
    df = preprocess_data(data)
    
    # Analyze the data
    severity_counts = df['Severity'].value_counts()
    effort_debt_analysis = analyze_effort_debt(df)
    component_distribution = analyze_component_distribution(df)
    rule_counts = rule_analysis(df)

    # Visualize the data
    visualize_data(severity_counts, effort_debt_analysis, component_distribution, rule_counts)
