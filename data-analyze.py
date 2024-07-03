import pandas as pd
import json
import matplotlib.pyplot as plt
import os

severity_colors = ['mediumaquamarine', 'orangered', 'mediumpurple']

def load_data(file_path):
    with open(file_path) as file:
        data = json.load(file)
    return data

def preprocess_data(data):
    records = []
    for project_key, project_data in data.items():
        for issue in project_data['issues']:
            records.append(issue)
    df = pd.DataFrame(records)
    df.columns = ['Issue Key', 'Rule', 'Severity', 'Component', 'Project', 'Line', 'Hash', 'Text Range',
                  'Flows', 'Status', 'Message', 'Effort', 'Debt', 'Author',
                  'Tags', 'Creation Date', 'Update Date', 'Issue Type', 'Scope']
    return df

def analyze_severity(df):
    severity_counts = df['Severity'].value_counts()
    return severity_counts

def analyze_effort_debt(df):
    df['Effort'] = pd.to_numeric(df['Effort'].str.replace('min', ''), errors='coerce')
    df['Debt'] = pd.to_numeric(df['Debt'].str.replace('min', ''), errors='coerce')
    effort_debt_analysis = df.groupby('Severity')[['Effort', 'Debt']].sum()
    return effort_debt_analysis

def analyze_component_distribution(df):
    component_distribution = df['Component'].value_counts()
    return component_distribution

def analyze_rule_distribution(df):
    df['Rule'] = df['Rule'].apply(lambda x: x.replace('dartanalyzer:', ''))
    rule_counts = df['Rule'].value_counts()
    return rule_counts

def analyze_code_lines(df, data):
    lines = []
    for project_key, project_data in data.items():
        metrics = project_data['metrics']['component']['measures']
        for metric in metrics:
            if metric['metric'] == 'ncloc':
                lines.append({'Project': project_key, 'Lines of Code': int(metric['value'])})
    df_lines = pd.DataFrame(lines)
    return df_lines

def analyze_complexity(df, data):
    complexity = []
    for project_key, project_data in data.items():
        metrics = project_data['metrics']['component']['measures']
        for metric in metrics:
            if metric['metric'] == 'complexity':
                complexity.append({'Project': project_key, 'Complexity': int(metric['value'])})
    df_complexity = pd.DataFrame(complexity)
    return df_complexity

def analyze_duplicated_lines_density(df, data):
    duplicated_lines = []
    for project_key, project_data in data.items():
        metrics = project_data['metrics']['component']['measures']
        for metric in metrics:
            if metric['metric'] == 'duplicated_lines_density':
                duplicated_lines.append({'Project': project_key, 'Duplicated Lines Density': float(metric['value'])})
    df_duplicated_lines = pd.DataFrame(duplicated_lines)
    return df_duplicated_lines

def create_bar_chart_severity(severity_counts, save_path):
    plt.figure(figsize=(10, 6))
    plt.bar(severity_counts.index, severity_counts, color=severity_colors)
    plt.title('Distribution of Severity Levels in Code Smells')
    plt.xlabel('Severity Levels')
    plt.ylabel('Count')
    plt.xticks(rotation=0)
    for i, count in enumerate(severity_counts):
        plt.text(i, count, count, ha='center', va='bottom')
    plt.savefig(os.path.join(save_path, 'severity_distribution.png'))
    plt.close()

def create_pie_chart_severity(severity_counts, save_path):
    plt.figure(figsize=(10, 6))
    plt.pie(severity_counts, labels=severity_counts.index, autopct='%1.1f%%', startangle=140, colors=severity_colors)
    plt.title('Proportion of Severity Levels in Code Smells')
    plt.savefig(os.path.join(save_path, 'severity_proportion.png'))
    plt.close()

def create_effort_debt_chart(effort_debt_analysis, save_path):
    plt.figure(figsize=(10, 6))
    effort_debt_analysis.plot(kind='bar', color=['lightblue', 'lightcoral'])
    plt.title('Effort and Debt Analysis by Severity Level')
    plt.xlabel('Severity Levels')
    plt.ylabel('Effort/Debt')
    plt.xticks(rotation=0)
    plt.legend(["Effort", "Debt"])
    plt.savefig(os.path.join(save_path, 'effort_debt_analysis.png'))
    plt.close()

def create_component_distribution_chart(component_distribution, save_path):
    plt.figure(figsize=(10, 6))
    component_distribution.plot(kind='bar', color='skyblue')
    plt.title('Issue Distribution by Component')
    plt.xlabel('Component')
    plt.ylabel('Issue Count')
    plt.xticks(rotation=90, ha='right')
    plt.savefig(os.path.join(save_path, 'component_distribution.png'))
    plt.close()

def create_rule_distribution_chart(rule_counts, save_path):
    plt.figure(figsize=(10, 6))
    rule_counts.plot(kind='bar', color='skyblue')
    plt.title('Frequency of Issue Rules')
    plt.xlabel('Rule')
    plt.ylabel('Count')
    plt.xticks(rotation=90)
    for i, count in enumerate(rule_counts):
        plt.text(i, count, f"{rule_counts.index[i]}\n{count}", ha='center', va='bottom', rotation=0, fontsize=8)
    plt.savefig(os.path.join(save_path, 'rule_distribution.png'))
    plt.close()

def create_code_lines_chart(df_lines, save_path):
    plt.figure(figsize=(10, 6))
    df_lines.plot(kind='bar', x='Project', y='Lines of Code', color='skyblue')
    plt.title('Lines of Code per Project')
    plt.xlabel('Project')
    plt.ylabel('Lines of Code')
    plt.xticks(rotation=90, ha='right')
    plt.savefig(os.path.join(save_path, 'lines_of_code.png'))
    plt.close()

def create_complexity_chart(df_complexity, save_path):
    plt.figure(figsize=(10, 6))
    df_complexity.plot(kind='bar', x='Project', y='Complexity', color='skyblue')
    plt.title('Code Complexity per Project')
    plt.xlabel('Project')
    plt.ylabel('Complexity')
    plt.xticks(rotation=90, ha='right')
    plt.savefig(os.path.join(save_path, 'complexity.png'))
    plt.close()

def create_duplicated_lines_density_chart(df_duplicated_lines, save_path):
    plt.figure(figsize=(10, 6))
    df_duplicated_lines.plot(kind='bar', x='Project', y='Duplicated Lines Density', color='skyblue')
    plt.title('Duplicated Lines Density per Project')
    plt.xlabel('Project')
    plt.ylabel('Duplicated Lines Density')
    plt.xticks(rotation=90, ha='right')
    plt.savefig(os.path.join(save_path, 'duplicated_lines_density.png'))
    plt.close()

def visualize_data(df, data, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    severity_counts = analyze_severity(df)
    effort_debt_analysis = analyze_effort_debt(df)
    component_distribution = analyze_component_distribution(df)
    rule_counts = analyze_rule_distribution(df)
    df_lines = analyze_code_lines(df, data)
    df_complexity = analyze_complexity(df, data)
    df_duplicated_lines = analyze_duplicated_lines_density(df, data)
    
    create_bar_chart_severity(severity_counts, save_path)
    create_pie_chart_severity(severity_counts, save_path)
    create_effort_debt_chart(effort_debt_analysis, save_path)
    create_component_distribution_chart(component_distribution, save_path)
    create_rule_distribution_chart(rule_counts, save_path)
    create_code_lines_chart(df_lines, save_path)
    create_complexity_chart(df_complexity, save_path)
    create_duplicated_lines_density_chart(df_duplicated_lines, save_path)

if __name__ == "__main__":
    file_path = 'json-files/fetched_issues_data.json'
    save_path = 'analysis_results'
    
    data = load_data(file_path)
    df = preprocess_data(data)
    visualize_data(df, data, save_path)
