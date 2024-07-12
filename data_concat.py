from config import DATA
import pandas as pd
import numpy as np

oecd_countries = [
    'aut', 'bel', 'can', 'chl', 'cze', 'deu', 'dnk', 'esp', 'est',
    'fin', 'fra', 'grc', 'hun', 'irl', 'isr', 'ita', 'jpn', 'kor',
    'ltu', 'mex', 'nld', 'nor', 'nzl', 'pol', 'svk', 'svn', 'swe',
    'tur'
]

mapping_values = {
    'dummy_1': {
        'aut': [11, 13], 'bel': [8, 9], 'can': [10, 12], 'chl': [8],
        'cze': [11], 'deu': [6, 8], 'dnk': [12], 'esp': [9],
        'est': [13, 14], 'fin': [9], 'fra': [9], 'grc': [8],
        'hun': [9], 'irl': [9, 10], 'isr': [9], 'ita': [9],
        'jpn': [10], 'kor': [8], 'ltu': [10], 'mex': [8],
        'nld': [13, 14], 'nor': [11], 'nzl': [7, 8], 'pol': [8],
        'svk': [9], 'svn': [11], 'swe': [14], 'tur': [10]
    },
    'dummy_0': {
        'aut': [10, 12], 'bel': [7, 8], 'can': [10, 11], 'chl': [7],
        'cze': [10], 'deu': [5, 7], 'dnk': [11], 'esp': [8],
        'est': [8], 'fin': [8], 'fra': [10], 'grc': [7],
        'hun': [8], 'irl': [8, 9], 'isr': [6], 'ita': [8],
        'jpn': [9], 'kor': [7], 'ltu': [9], 'mex': [7],
        'nld': [12, 13], 'nor': [10], 'nzl': [12, 13], 'pol': [7],
        'svk': [8], 'svn': [9], 'swe': [14], 'tur': [8]
    }
}

relevant_columns = [
    'dummy_bachelor', 'b_q01a', 'b_q03b', 'b_q12b', 'b_q12d', 
    'b_q12f', 'b_q12h', 'd_q16d1', 'd_q16d2', 'd_q16d3', 
    'd_q16d4', 'd_q16d5', 'd_q16d6'
]

# Create the mapping rules dictionary
mapping_rules = {}
for country in oecd_countries:
    mapping_rules[country.upper()] = {
        "dummy_1": [("b_q01a", mapping_values['dummy_1'][country])],
        "dummy_0": [("b_q03b", mapping_values['dummy_0'][country])]
    }

# Function to create dummy variable
def create_dummy_variable(df, dataset_name):
    # Initialize dummy variable column with NaN
    df['dummy_bachelor'] = np.nan

    # Apply the mapping rules for the given dataset
    if dataset_name in mapping_rules:
        rules = mapping_rules[dataset_name]
        
        # Set dummy to 1
        for col, values in rules["dummy_1"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df.loc[df[col].isin(values), 'dummy_bachelor'] = 1
        
        # Set dummy to 0
        for col, values in rules["dummy_0"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df.loc[df[col].isin(values), 'dummy_bachelor'] = 0

    return df


def load_country_data(country_code, data_path, relevant_columns):
    """
    Load data for a specific country.
    
    Args:
        country_code (str): The country code.
        data_path (Path): The path to the data files.
    
    Returns:
        pd.DataFrame: The loaded DataFrame.
    """
    file_path = data_path / f'prg{country_code}p1.csv'
    df = pd.read_csv(file_path, low_memory=False)
    df.columns = df.columns.str.lower()
    df = create_dummy_variable(df, country_code.upper())
    df = df[[col for col in relevant_columns if col in df.columns]]
    return df


def concatenate_country_data(countries, data_path):
    """
    Concatenate data for a list of countries.
    
    Args:
        countries (list): List of country codes.
        data_path (Path): The path to the data files.
    
    Returns:
        pd.DataFrame: The concatenated DataFrame.
    """
    df_concat = pd.DataFrame()
    for country in countries:
        df = load_country_data(country, data_path, relevant_columns)
        df_concat = pd.concat([df_concat, df], ignore_index=True)
        print(f'{country}: {df.shape}')
    return df_concat

def save_concatenated_data(df, output_path):
    """
    Save the concatenated DataFrame to a Parquet file.
    
    Args:
        df (pd.DataFrame): The DataFrame to save.
        output_path (Path): The path to save the Parquet file.
    """
    df.to_parquet(output_path, index=False)
    print(f'Saved concatenated data to {output_path}')

def main():
    """
    Main function to load, concatenate, and save data for OECD countries.
    """
    data_path = DATA
    output_file = data_path / 'prgoecd.parquet'
    
    df_concat = concatenate_country_data(oecd_countries, data_path)
    save_concatenated_data(df_concat, output_file)

if __name__ == "__main__":
    main()