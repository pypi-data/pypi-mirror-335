import os
import pandas as pd
import numpy as np
import math

def i10_index(citationSeries):
    """Calculate i10 index."""
    i10 = sum(1 for c in sorted(citationSeries, reverse=True) if c >= 10)
    return i10

def h_index(citationSeries):
    """Calculate h-index."""
    h = sum(1 for i, c in enumerate(sorted(citationSeries, reverse=True)) if c >= i + 1)
    return h

def e_index(citationSeries, hIndex):
    """Calculate e-index."""
    citations = sorted(citationSeries, reverse=True)
    totalCitations = sum(citations[:hIndex])
    return (totalCitations - hIndex**2) ** 0.5

def g_index(citationSeries):
    """Calculate g-index."""
    citations = sorted(citationSeries, reverse=True)
    g, totalCitations = 0, 0
    for c in citations:
        totalCitations += c
        if totalCitations >= (g + 1) ** 2:
            g += 1
        else:
            break
    return g

def s_index(citationSeries, totalCitations, totalPapers):
    """Calculate s-index."""
    if totalCitations == 0:
        return 0
    p_values = [c / totalCitations for c in citationSeries if c > 0]
    S = -sum(p * np.log(p) for p in p_values)
    S0 = math.log(totalPapers)
    return 0.25 * (totalCitations ** 0.5) * math.exp(S / S0)

def calculate_entropy(citations):
    """Calculate entropy."""
    total_citations = sum(citations)
    if total_citations == 0:
        return 0
    probabilities = [c / total_citations for c in citations if c > 0]
    return -sum(p * np.log(p) for p in probabilities)

def calculate_t_index(citations, h_indices):
    """Calculate t-index."""
    N = len(citations)
    if N == 0:
        return 0
    average_h_index = np.mean(h_indices)
    entropy_T = calculate_entropy(citations)
    normalization_factor = np.log(10 * N)
    consistency_u = np.exp(entropy_T / normalization_factor)
    return 4 * average_h_index * consistency_u

def process_csv_files(directory):
    """Process all CSV files in a given directory."""
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return
    
    records = {}

    for file in csv_files:
        file_path = os.path.join(directory, file)
        print(f"Processing: {file_path}")
        
        df = pd.read_csv(file_path, usecols=['EID', 'Year', 'Cited by', 'Document Type', 'Funding Details'])
        df.set_index('EID', drop=False, inplace=True, verify_integrity=True)

        total_citations = df['Cited by'].sum()
        total_papers = len(df)

        data = {
            'Quantity of Publications': total_papers,
            'Total Citations': total_citations,
            'Average Citations per Paper (C/P)': total_citations / total_papers if total_papers else 0,
            'i10 Index': i10_index(df['Cited by']),
            'h index': h_index(df['Cited by']),
            'Mock_h index': ((total_citations ** 2) / total_papers) ** (1 / 3) if total_papers else 0,
            'e index': e_index(df['Cited by'], h_index(df['Cited by'])),
            'm index': h_index(df['Cited by']) / (2024 - df['Year'].min()) if not df['Year'].isna().all() else 0,
            'g index': g_index(df['Cited by']),
            's index': s_index(df['Cited by'], total_citations, total_papers),
            'Funding Details': df['Funding Details'].notna().sum()
        }

        yearly_citations = df.groupby('Year')['Cited by'].sum()
        yearly_h_indices = [h_index(df[df['Year'] == year]['Cited by']) for year in yearly_citations.index]
        data['t index'] = calculate_t_index(yearly_citations.tolist(), yearly_h_indices)

        doctype_counts = df['Document Type'].value_counts().to_dict()
        data.update(doctype_counts)

        records[file.replace('.csv', '')] = data

    save_results(directory, records)

def save_results(directory, records):
    """Save the processed records into CSV files."""
    output_dir = os.path.join(directory, 'Output_main')
    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame.from_dict(records, orient='index')
    df.fillna(0, inplace=True)

    df.to_csv(os.path.join(output_dir, 'indices.csv'))
    print(f"Output saved to: {output_dir}\\indices.csv")

def run():
    """Main function to execute the package."""
    directory = input("Enter the path to your data directory: ").strip()
    if not os.path.exists(directory):
        print("Invalid directory. Please provide a valid path.")
        return
    process_csv_files(directory)


def hello_world():
    return "Hello World!"








