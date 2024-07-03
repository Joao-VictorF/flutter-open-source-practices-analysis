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

def extract_project_and_filename(component):
    # Divide o componente pelo separador ':' e considera apenas a última parte (o nome do arquivo)
    # e a primeira parte antes do ':', que é o nome do projeto
    parts = component.split(':')
    if len(parts) > 1:
        project_name = parts[0]
        filename = parts[-1].split('/')[-1]
        return f"{project_name}/{filename}"
    else:
        return component

def analyze_component_distribution(df):
    df['Simplified Component'] = df['Component'].apply(extract_project_and_filename)
    component_distribution = df['Simplified Component'].value_counts()
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
        complexity_value = next((int(metric['value']) for metric in metrics if metric['metric'] == 'complexity'), None)
        if complexity_value is not None:
            complexity.append({'Project': project_key, 'Complexity': complexity_value})
    df_complexity = pd.DataFrame(complexity)
    return df_complexity

def analyze_duplicated_lines_density(df, data):
    duplicated_lines = []
    for project_key, project_data in data.items():
        metrics = project_data['metrics']['component']['measures']
        duplicated_density_value = next((float(metric['value']) for metric in metrics if metric['metric'] == 'duplicated_lines_density'), None)
        if duplicated_density_value is not None and duplicated_density_value > 0:
            duplicated_lines.append({'Project': project_key, 'Duplicated Lines Density': duplicated_density_value})
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
    plt.figure(figsize=(10, 12))  # Aumenta a altura da figura para caber todos os nomes dos componentes
    top_components = component_distribution.nlargest(20)  # Mostra os 20 componentes com mais problemas
    top_components.sort_values(ascending=True, inplace=True)
    top_components.plot(kind='barh', color='skyblue', ax=plt.gca())
    plt.title('Top 20 Components by Issue Count')
    plt.xlabel('Issue Count')
    plt.ylabel('Component')
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes
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
    plt.figure(figsize=(10, 12))  # Aumenta a altura da figura para caber todos os nomes dos projetos
    df_complexity.sort_values(by='Complexity', ascending=True, inplace=True)
    ax = df_complexity.plot(kind='barh', x='Project', y='Complexity', color='skyblue', ax=plt.gca())
    plt.title('Code Complexity per Project')
    plt.xlabel('Complexity')
    plt.ylabel('Project')
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes

    # Adiciona os valores nas barras
    for index, value in enumerate(df_complexity['Complexity']):
        ax.text(value + 1, index, f"{value:.2f}", va='center', ha='left')
    
    plt.savefig(os.path.join(save_path, 'complexity.png'))
    plt.close()


def create_duplicated_lines_density_chart(df_duplicated_lines, save_path):
    plt.figure(figsize=(10, 12))
    df_duplicated_lines.sort_values(by='Duplicated Lines Density', ascending=True, inplace=True)
    ax = df_duplicated_lines.plot(kind='barh', x='Project', y='Duplicated Lines Density', color='skyblue', ax=plt.gca())
    plt.title('Duplicated Lines Density per Project (> 0)')
    plt.xlabel('Duplicated Lines Density')
    plt.ylabel('Project')
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes
    
    # Adiciona os valores nas barras
    for index, value in enumerate(df_duplicated_lines['Duplicated Lines Density']):
        ax.text(value + 0.1, index, f"{value:.2f}", va='center', ha='left')
    
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
