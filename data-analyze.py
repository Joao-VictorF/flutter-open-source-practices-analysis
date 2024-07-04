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

def extract_project_and_filename(component):
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
    rule_counts = df['Rule'].value_counts()
    total_issues = rule_counts.sum()
    cumulative_percentage = rule_counts.cumsum() / total_issues
    top_rules = rule_counts[cumulative_percentage <= 0.70]
    return top_rules

def analyze_code_lines(df, data):
    lines_of_code = []
    for project_key, project_data in data.items():
        metrics = project_data['metrics']['component']['measures']
        loc_value = next((int(metric['value']) for metric in metrics if metric['metric'] == 'ncloc'), None)
        if loc_value is not None:
            lines_of_code.append({'Project': project_key, 'Lines of Code': loc_value})
    df_lines_of_code = pd.DataFrame(lines_of_code)
    return df_lines_of_code

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
    plt.title("VBP's por Severidade")
    plt.xlabel('Severidade')
    plt.xticks(rotation=0)
    for i, count in enumerate(severity_counts):
        plt.text(i, count, count, ha='center', va='bottom')
    plt.savefig(os.path.join(save_path, 'severity_distribution.png'))
    plt.close()

def create_pie_chart_severity(severity_counts, save_path):
    plt.figure(figsize=(10, 6))
    plt.pie(severity_counts, labels=severity_counts.index, autopct='%1.1f%%', startangle=140, colors=severity_colors)
    plt.title("VBP's por Severidade (%)")
    plt.savefig(os.path.join(save_path, 'severity_proportion.png'))
    plt.close()

def create_component_distribution_chart(component_distribution, save_path):
    plt.figure(figsize=(10, 12))  # Aumenta a altura da figura para caber todos os nomes dos componentes
    top_components = component_distribution.nlargest(20)  # Mostra os 20 componentes com mais problemas
    top_components.sort_values(ascending=False, inplace=True)
    ax = top_components.plot(kind='barh', color='skyblue', ax=plt.gca())
    plt.title("Top 20 componentes com mais casos de VBP's")
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes

    # Adiciona os valores nas barras
    for index, value in enumerate(top_components):
        ax.text(value + 0.5, index, f"{value}", va='center', ha='left')

    plt.savefig(os.path.join(save_path, 'component_distribution.png'))
    plt.close()

def create_rule_distribution_chart(rule_distribution, save_path):
    plt.figure(figsize=(10, 8))  # Aumenta a altura da figura para caber todos os nomes das regras
    ax = rule_distribution.plot(kind='barh', color='skyblue', ax=plt.gca())
    plt.title('Regras mais violadas (70% dos casos de VBP)')
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes

    # Adiciona os valores nas barras
    for index, value in enumerate(rule_distribution):
        ax.text(value, index, f"{value}", va='center', ha='right')
    
    plt.savefig(os.path.join(save_path, 'rule_distribution.png'))
    plt.close()

def create_code_lines_chart(df_lines_of_code, save_path):
    plt.figure(figsize=(10, 12))  # Aumenta a altura da figura para caber todos os nomes dos projetos
    df_lines_of_code.sort_values(by='Lines of Code', ascending=False, inplace=True)
    ax = df_lines_of_code.plot(kind='barh', x='Project', y='Lines of Code', color='skyblue', ax=plt.gca())
    plt.title('Linhas de Código por Projeto')
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes

    # Adiciona os valores nas barras
    # for index, value in enumerate(df_lines_of_code['Lines of Code']):
    #     ax.text(value + 10, index, f"{value}", va='center', ha='left')

    plt.savefig(os.path.join(save_path, 'lines_of_code.png'))
    plt.close()

def create_complexity_chart(df_complexity, save_path):
    plt.figure(figsize=(10, 12))  # Aumenta a altura da figura para caber todos os nomes dos projetos
    df_complexity.sort_values(by='Complexity', ascending=False, inplace=True)
    ax = df_complexity.plot(kind='barh', x='Project', y='Complexity', color='skyblue', ax=plt.gca())
    plt.title('Complexidade Ciclomática por Projeto')
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes

    # Adiciona os valores nas barras
    for index, value in enumerate(df_complexity['Complexity']):
        ax.text(value + 1, index, f"{value:.2f}", va='center', ha='left')
    
    plt.savefig(os.path.join(save_path, 'complexity.png'))
    plt.close()

def create_duplicated_lines_density_chart(df_duplicated_lines, save_path):
    plt.figure(figsize=(10, 12))
    df_duplicated_lines.sort_values(by='Duplicated Lines Density', ascending=False, inplace=True)
    ax = df_duplicated_lines.plot(kind='barh', x='Project', y='Duplicated Lines Density', color='skyblue', ax=plt.gca())
    plt.title('Densidade de Linhas Duplicadas por Projeto (%) (> 0)')
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes
    
    # Adiciona os valores nas barras
    for index, value in enumerate(df_duplicated_lines['Duplicated Lines Density']):
        ax.text(value + 0.1, index, f"{value:.2f}", va='center', ha='left')
    
    plt.savefig(os.path.join(save_path, 'duplicated_lines_density.png'))
    plt.close()

def save_summary_to_json(severity_counts, component_distribution, rule_counts, df_lines_of_code, df_complexity, df_duplicated_lines, save_path):
    summary = {
        'severity_counts': severity_counts.to_dict(),
        'top_components': component_distribution.nlargest(20).to_dict(),
        'top_rules': rule_counts.to_dict(),
        'lines_of_code': df_lines_of_code.to_dict(orient='records'),
        'complexity': df_complexity.to_dict(orient='records'),
        'duplicated_lines_density': df_duplicated_lines.to_dict(orient='records')
    }
    with open(os.path.join(save_path, 'summary.json'), 'w') as file:
        json.dump(summary, file, indent=4)

def visualize_data(df, data, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    severity_counts = analyze_severity(df)
    component_distribution = analyze_component_distribution(df)
    rule_counts = analyze_rule_distribution(df)
    df_lines_of_code = analyze_code_lines(df, data)
    df_complexity = analyze_complexity(df, data)
    df_duplicated_lines = analyze_duplicated_lines_density(df, data)
    
    create_bar_chart_severity(severity_counts, save_path)
    create_pie_chart_severity(severity_counts, save_path)
    create_component_distribution_chart(component_distribution, save_path)
    create_rule_distribution_chart(rule_counts, save_path)
    create_code_lines_chart(df_lines_of_code, save_path)
    create_complexity_chart(df_complexity, save_path)
    create_duplicated_lines_density_chart(df_duplicated_lines, save_path)
    save_summary_to_json(severity_counts, component_distribution, rule_counts, df_lines_of_code, df_complexity, df_duplicated_lines, save_path)

if __name__ == "__main__":
    file_path = 'json-files/fetched_issues_data.json'
    save_path = 'analysis_results'
    
    data = load_data(file_path)
    df = preprocess_data(data)
    visualize_data(df, data, save_path)