import pandas as pd
import json
import matplotlib.pyplot as plt
import os
from scipy.stats import pearsonr

severity_colors = ['mediumaquamarine', 'orangered', 'mediumpurple']
rule_abbreviations = {
    'dartanalyzer:exhaustive_cases': 'EC',
    'dartanalyzer:always_declare_return_types': 'ADRT',
    'dartanalyzer:constant_identifier_names': 'CIN',
    'dartanalyzer:non_constant_identifier_names': 'NCIN',
    'dartanalyzer:depend_on_referenced_packages': 'DRP',
    'dartanalyzer:prefer_void_to_null': 'PVTN',
    'dartanalyzer:library_private_types_in_public_api': 'LPTPA',
    'dartanalyzer:no_leading_underscores_for_local_identifiers': 'NLULI',
    'dartanalyzer:avoid_function_literals_in_foreach_calls': 'AFLFC'
}

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
    return rule_counts.head(5)
    # Top 70% of violated rules
    # total_issues = rule_counts.sum()
    # cumulative_percentage = rule_counts.cumsum() / total_issues
    # top_rules = rule_counts[cumulative_percentage <= 0.70]
    # return top_rules

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

def normalize_project_name(name):
    return name.replace(':', '/')

def analyze_vbps_vs_ncloc(df, df_lines_of_code):
    # Normalize project names in both dataframes
    df['Project'] = df['Project'].apply(normalize_project_name)
    df_lines_of_code['Project'] = df_lines_of_code['Project'].apply(normalize_project_name)
    
    # Count VBPs per project
    vbp_counts = df['Project'].value_counts().reset_index()
    vbp_counts.columns = ['Project', 'VBP Count']
    
    # Merge VBP counts with lines of code
    merged_df = pd.merge(vbp_counts, df_lines_of_code, on='Project', how='inner')
    
    if not merged_df.empty:
        # Calculate VBPs per 1000 lines of code
        merged_df['VBPs per 1000 LCNC'] = (merged_df['VBP Count'] / merged_df['Lines of Code']) * 1000
    
    return merged_df

def analyze_vbps_vs_complexity(df, df_complexity):
    # Normalize project names in both dataframes
    df['Project'] = df['Project'].apply(normalize_project_name)
    df_complexity['Project'] = df_complexity['Project'].apply(normalize_project_name)
    
    # Count VBPs per project
    vbp_counts = df['Project'].value_counts().reset_index()
    vbp_counts.columns = ['Project', 'VBP Count']
    
    # Merge VBP counts with complexity
    merged_df = pd.merge(vbp_counts, df_complexity, on='Project', how='inner')
    
    return merged_df

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
    # Mapeia os nomes completos das regras para suas siglas
    rule_distribution.index = rule_distribution.index.map(rule_abbreviations)
    
    plt.figure(figsize=(10, 8))  # Aumenta a altura da figura para caber todos os nomes das regras
    ax = rule_distribution.plot(kind='barh', color='skyblue', ax=plt.gca())
    plt.title('Top 5 Regras mais violadas', fontsize=20)
    plt.xlabel('Número de VBPs', fontsize=20)
    plt.ylabel('Regras', fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes

    # Adiciona os valores nas barras
    for index, value in enumerate(rule_distribution):
        ax.text(value, index, f"{value}", va='center', ha='right', fontsize=20)
    
    plt.savefig(os.path.join(save_path, 'rule_distribution.png'))
    plt.close()

def create_code_lines_chart(df_lines_of_code, save_path):
    plt.figure(figsize=(10, 12))  # Aumenta a altura da figura para caber todos os nomes dos projetos
    df_lines_of_code.sort_values(by='Lines of Code', ascending=False, inplace=True)
    ax = df_lines_of_code.plot(kind='barh', x='Project', y='Lines of Code', color='skyblue', ax=plt.gca())
    plt.title('Linhas de Código por Projeto')
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes

    plt.savefig(os.path.join(save_path, 'lines_of_code.png'))
    plt.close()

def create_complexity_chart(df_complexity, save_path):
    plt.figure(figsize=(10, 12))  # Aumenta a altura da figura para caber todos os nomes dos projetos
    df_complexity.sort_values(by='Complexity', ascending=False, inplace=True)
    ax = df_complexity.plot(kind='barh', x='Project', y='Complexity', color='skyblue', ax=plt.gca())
    plt.title('Complexidade Ciclomática por Projeto')
    plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes

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
    
    for index, value in enumerate(df_duplicated_lines['Duplicated Lines Density']):
        ax.text(value + 0.1, index, f"{value:.2f}", va='center', ha='left')
    
    plt.savefig(os.path.join(save_path, 'duplicated_lines_density.png'))
    plt.close()

def create_vbps_vs_ncloc_chart(df_vbps_vs_ncloc, save_path):
    if df_vbps_vs_ncloc.empty:
        print("No data available for VBPs vs LCNC chart.")
        return
    plt.figure(figsize=(10, 12))
    df_vbps_vs_ncloc.sort_values(by='VBPs per 1000 LCNC', ascending=False, inplace=True)
    ax = df_vbps_vs_ncloc.plot(kind='barh', x='Project', y='VBPs per 1000 LCNC', color='skyblue', ax=plt.gca())
    plt.title('VBPs por 1000 Linhas de Código por Projeto')
    plt.tight_layout()
    
    for index, value in enumerate(df_vbps_vs_ncloc['VBPs per 1000 LCNC']):
        ax.text(value + 0.1, index, f"{value:.2f}", va='center', ha='left')
    
    plt.savefig(os.path.join(save_path, 'vbps_per_1000_loc.png'))
    plt.close()

def create_vbps_vs_complexity_chart(df_vbps_vs_complexity, save_path):
    if df_vbps_vs_complexity.empty:
        print("No data available for VBPs vs Complexity chart.")
        return
    plt.figure(figsize=(10, 12))
    df_vbps_vs_complexity.sort_values(by='Complexity', ascending=False, inplace=True)
    ax = df_vbps_vs_complexity.plot(kind='barh', x='Project', y='VBP Count', color='skyblue', ax=plt.gca())
    plt.title('VBPs por Projeto em Relação à Complexidade')
    plt.xlabel('Número de VBPs')
    plt.ylabel('Projetos')
    plt.tight_layout()
    
    for index, value in enumerate(df_vbps_vs_complexity['VBP Count']):
        ax.text(value + 0.1, index, f"{value}", va='center', ha='left')
    
    plt.savefig(os.path.join(save_path, 'vbps_vs_complexity.png'))
    plt.close()

def calculate_correlation(df, x, y):
    correlation, _ = pearsonr(df[x], df[y])
    return correlation

def create_scatter_plot(df, x, y, title, xlabel, ylabel, save_path):
    plt.figure(figsize=(10, 6))
    plt.scatter(df[x], df[y], color='skyblue')
    plt.title(title, fontsize=20)
    plt.xlabel(xlabel, fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.grid(True)
    plt.savefig(os.path.join(save_path, f"{title.replace(' ', '_').lower()}.png"))
    plt.close()

def save_summary_to_json(summary, save_path):
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
    df_vbps_vs_ncloc = analyze_vbps_vs_ncloc(df, df_lines_of_code)
    df_vbps_vs_complexity = analyze_vbps_vs_complexity(df, df_complexity)
    
    create_bar_chart_severity(severity_counts, save_path)
    create_pie_chart_severity(severity_counts, save_path)
    create_component_distribution_chart(component_distribution, save_path)
    create_rule_distribution_chart(rule_counts, save_path)
    create_code_lines_chart(df_lines_of_code, save_path)
    create_complexity_chart(df_complexity, save_path)
    create_duplicated_lines_density_chart(df_duplicated_lines, save_path)
    create_vbps_vs_ncloc_chart(df_vbps_vs_ncloc, save_path)
    create_vbps_vs_complexity_chart(df_vbps_vs_complexity, save_path)
    
    # Calculate correlations
    if not df_vbps_vs_ncloc.empty:
        correlation_vbp_loc = calculate_correlation(df_vbps_vs_ncloc, 'Lines of Code', 'VBP Count')
        create_scatter_plot(df_vbps_vs_ncloc, 'Lines of Code', 'VBP Count', 'Correlação entre VBPs e LCNC', 'Linhas de Código Não Comentadas', 'Número de VBPs', save_path)
    else:
        correlation_vbp_loc = None

    if not df_vbps_vs_complexity.empty:
        correlation_vbp_complexity = calculate_correlation(df_vbps_vs_complexity, 'Complexity', 'VBP Count')
        create_scatter_plot(df_vbps_vs_complexity, 'Complexity', 'VBP Count', 'Correlação entre VBPs e Complexidade Ciclomática', 'Complexidade', 'Número de VBPs', save_path)
    else:
        correlation_vbp_complexity = None
    
    summary = {
        'severity_counts': severity_counts.to_dict(),
        'top_components': component_distribution.nlargest(20).to_dict(),
        'top_rules': rule_counts.to_dict(),
        'lines_of_code': df_lines_of_code.to_dict(orient='records'),
        'complexity': df_complexity.to_dict(orient='records'),
        'duplicated_lines_density': df_duplicated_lines.to_dict(orient='records'),
        'vbps_vs_ncloc': df_vbps_vs_ncloc.to_dict(orient='records'),
        'vbps_vs_complexity': df_vbps_vs_complexity.to_dict(orient='records'),
        'correlation_vbp_loc': correlation_vbp_loc,
        'correlation_vbp_complexity': correlation_vbp_complexity
    }
    
    save_summary_to_json(summary, save_path)

if __name__ == "__main__":
    file_path = 'json-files/fetched_issues_data.json'
    save_path = 'analysis_results'
    
    data = load_data(file_path)
    df = preprocess_data(data)
    visualize_data(df, data, save_path)
