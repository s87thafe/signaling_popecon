from config import DATA
import plotly.express as px
import pandas as pd
import numpy as np
import statsmodels.api as sm

# # Load the data
# list_of_countries = [
#     'aut', 'bel', 'can', 'chl', 'cze', 'deu', 'dnk', 'ecu', 'esp', 'est',
#     'fin', 'fra', 'gbr', 'grc', 'hun', 'irl', 'isr', 'ita', 'jpn', 'kaz',
#     'kor', 'ltu', 'mex', 'nld', 'nor', 'nzl', 'per', 'pol', 'rus', 'sgp',
#     'svk', 'svn', 'swe', 'tur', 'usa'
# ]

# # Initialize an empty dictionary to hold the frequencies for each country
# country_frequencies = {country: {} for country in list_of_countries}

# # Function to calculate frequency of each value for specified variables in a DataFrame
# def calculate_frequencies(data, variables):
#     frequencies = {val: 0 for val in ['N', 'V', 'R', 1, 2, 3, 4, 5, 6]}
#     for var in variables:
#         if var in data.columns:
#             value_counts = data[var].value_counts()
#             for value, count in value_counts.items():
#                 if value in frequencies:
#                     frequencies[value] += count
#                 else:
#                     frequencies[value] = count
#     return frequencies

# # Iterate through each country and calculate frequencies
# for country in list_of_countries:
#     data = pd.read_csv(f"{DATA}/prg{country}p1.csv", low_memory=False)
#     variables = [f'D_Q16d{i}' for i in range(1, 7)]
#     country_frequencies[country] = calculate_frequencies(data, variables)

# # Convert the result to a DataFrame for better visualization
# frequency_df = pd.DataFrame(country_frequencies).transpose()

df = pd.read_csv(DATA/'prgsvnp1.csv', low_memory=False)

# Mapping hourly, daily, weekly, bi-weekly, monthly, and yearly wages
hourly_wage = {
    '1': 4.50, 
    '2': 5.50, 
    '3': 7.50, 
    '4': 10.50, 
    '5': 15.00, 
    '6': 20.50  # 15.00 + (15.00 - 10.50)
}

daily_wage = {
    '1': 35.00, 
    '2': 42.00, 
    '3': 58.00, 
    '4': 84.00, 
    '5': 120.00, 
    '6': 156.00  # 120.00 + (120.00 - 84.00)
}

weekly_wage = {
    '1': 170.00, 
    '2': 210.00, 
    '3': 290.00, 
    '4': 420.00, 
    '5': 590.00, 
    '6': 760.00  # 590.00 + (590.00 - 420.00)
}

biweekly_wage = {
    '1': 340.00, 
    '2': 420.00, 
    '3': 580.00, 
    '4': 840.00, 
    '5': 1180.00, 
    '6': 1520.00  # 1180.00 + (1180.00 - 840.00)
}

monthly_wage = {
    '1': 750.00, 
    '2': 900.00, 
    '3': 1250.00, 
    '4': 1800.00, 
    '5': 2550.00, 
    '6': 3300.00  # 2550.00 + (2550.00 - 1800.00)
}

yearly_wage = {
    '1': 18000.00, 
    '2': 21600.00, 
    '3': 31200.00, 
    '4': 38400.00, 
    '5': 51000.00, 
    '6': 63600.00  # 51000.00 + (51000.00 - 38400.00)
}
# Ensure that the relevant columns are treated as strings to avoid dtype issues
for col in ['D_Q16d1', 'D_Q16d2', 'D_Q16d3', 'D_Q16d4', 'D_Q16d5', 'D_Q16d6']:
    df[col] = df[col].replace(['V', 'D', 'R'], np.nan)
    df[col] = df[col].astype(str)

def calculate_monthly_wage(row):
    if row['D_Q16d1'] in hourly_wage:
        return hourly_wage[row['D_Q16d1']] * 174
    elif row['D_Q16d2'] in daily_wage:
        return daily_wage[row['D_Q16d2']] * 22
    elif row['D_Q16d3'] in weekly_wage:
        return weekly_wage[row['D_Q16d3']] * 4
    elif row['D_Q16d4'] in biweekly_wage:
        return biweekly_wage[row['D_Q16d4']] * 2
    elif row['D_Q16d5'] in monthly_wage:
        return monthly_wage[row['D_Q16d5']]
    elif row['D_Q16d6'] in yearly_wage:
        return yearly_wage[row['D_Q16d6']] / 12
    else:
        return np.nan

df['monthly_wage'] = df.apply(calculate_monthly_wage, axis=1)

print(df['monthly_wage'].describe())

# Year of the data
current_year = 2012

# Generate Variables for Dropout
df['Dropout_BA'] = (df['B_Q03b'] == 9)
df['Dropout_MA'] = (df['B_Q03b'] == 11)
df['Dropout_PhD'] = (df['B_Q03b'] == 12)

print(df['Dropout_BA'].value_counts())
print(df['Dropout_MA'].value_counts())
print(df['Dropout_PhD'].value_counts())

# Generate Variables for Attainers
df['Attainers_BA'] = (df['B_Q01a'] == 9)
df['Attainers_MA'] = (df['B_Q01a'] == 11)
df['Attainers_PhD'] = (df['B_Q01a'] == 12)

# Ensure that the relevant columns are treated as strings to avoid dtype issues
for col in ['B_Q03c2', 'B_Q01c2']:
    df[col] = df[col].replace(['V', 'D', 'R'], np.nan)
    df[col] = df[col].astype(str)

# # Date of dropout or attainment
# for grade in ['BA', 'MA', 'PhD']:
#     df[f'Dropout_{grade}_date'] = df['B_Q03c2'].where(df[f'Dropout_{grade}'], None)
#     df[f'Attainers_{grade}_date'] = df['B_Q01c2'].where(df[f'Attainers_{grade}'], None)

# # Calculate the time since dropout or attainment
# for grade in ['BA', 'MA', 'PhD']:
#     df[f'Time_since_Dropout_{grade}'] = current_year - df[f'Dropout_{grade}_date'].astype(float)
#     df[f'Time_since_Attainers_{grade}'] = current_year - df[f'Attainers_{grade}_date'].astype(float)

# # Prepare data for plotting
# plot_data = pd.DataFrame()
# for grade in ['BA', 'MA', 'PhD']:
#     for status in ['Dropout', 'Attainers']:
#         temp_data = df[df[f'{status}_{grade}']].copy()
#         temp_data['Status'] = status
#         temp_data['Time_since'] = temp_data[f'Time_since_{status}_{grade}']
#         temp_data['Wage'] = temp_data['monthly_wage']
#         plot_data = pd.concat([plot_data, temp_data[['Wage', 'Time_since', 'Status']]])

# # Plotting with Plotly
# fig = px.scatter(plot_data, x='Time_since', y='Wage', color='Status', 
#                  title='Wages of Degree Attainers and Dropouts Over Time',
#                  labels={'Wage': 'Wage ($)', 'Time_since': 'Time Since Dropout/Attainment (years)', 'Status': 'Education Status'},
#                  trendline="ols")

# fig.show()

# def variable_describer(varname, data=data):
#     data_unique = data[varname].unique()
#     data_frequency = data[varname].value_counts()
#     # print(data_unique)
#     print(data_frequency)
#     # print(data[varname].describe())

# for i in [1, 2, 3, 4, 5, 6]:
#     variable_describer(f'D_Q16d{i}', data=df)