from config import DATA, IMAGES
import pandas as pd
import plotly.figure_factory as ff
import statsmodels.api as sm
from statsmodels.sandbox.regression.gmm import IV2SLS
import plotly.express as px

# Read the parquet file
df = pd.read_parquet(DATA / 'prgoecd.parquet', engine='pyarrow')

# Copy the DataFrame
df_iv = df.copy()

# Columns of interest
wage_columns = ['d_q16d1', 'd_q16d2', 'd_q16d3', 'd_q16d4', 'd_q16d5', 'd_q16d6']
trainings_columns = ['b_q12b', 'b_q12f', 'b_q12h']

# Function to filter out non-numeric values
def filter_numeric(series):
    return pd.to_numeric(series, errors='coerce')

# Apply the filter_numeric function to the wage columns
df_iv[wage_columns] = df_iv[wage_columns].apply(filter_numeric)

# Create 'wage' column with the first non-NaN numeric value from the specified columns
df_iv['wage'] = df_iv[wage_columns].bfill(axis=1).iloc[:, 0]
df_iv['trainings_completed'] = df_iv[wage_columns].bfill(axis=1).iloc[:, 0]

# Drop the original wage columns
df_iv = df_iv.drop(columns=wage_columns)

df_iv = df_iv.dropna(subset=['wage', 'dummy_bachelor', 'trainings_completed'])

# Generate Descroptive Statistics
# Compute summary statistics
descriptive_stats = df_iv[['wage', 'dummy_bachelor', 'trainings_completed']].describe()

# Display the statistics
print(descriptive_stats)

# Prepare data for distplot with proper labels
group_labels = ['Bachelor Degree', 'Dropped Out']
hist_data = [df_iv[df_iv['dummy_bachelor'] == 1]['wage'].dropna().tolist(),
             df_iv[df_iv['dummy_bachelor'] == 0]['wage'].dropna().tolist()]

# Create distplot
fig = ff.create_distplot(hist_data, group_labels, curve_type='kde', show_hist=False, show_rug=False)

# Update the layout for better visualization
fig.update_layout(
    title='Kernel Density Estimation of Wage Grouped by Dummy Bachelor Status',
    xaxis_title='Wage',
    yaxis_title='Density',
    legend_title='Education Status',
    font=dict(size=12)
)
fig.write_image(IMAGES / 'distplot_wage.png')

# # Scatter plot with regression line
# fig = px.scatter(df_iv, x='dummy_bachelor', y='wage', trendline='ols', labels={'dummy_bachelor':'Bachelor Degree (1: Yes, 0: No)', 'wage':'Wage'})
# fig.update_layout(title='Relationship between Wage and Bachelor Degree',
#                   xaxis_title='Bachelor Degree (Dummy)',
#                   yaxis_title='Wage')
# fig.write_image(IMAGES / 'scatterplot_wage_bachelor.png')

# IV Regression: Using 'trainings_completed' as the instrument for 'dummy_bachelor'
# Endogenous variable: 'dummy_bachelor'
# Instrumental variable: 'trainings_completed'
# Dependent variable: 'wage'
iv_model = IV2SLS(df_iv['wage'], sm.add_constant(df_iv[['dummy_bachelor']]), df_iv[['trainings_completed']]).fit()

print(iv_model.summary())

# First Stage Regression: Checking the strength of the instrument
first_stage = sm.OLS(df_iv['dummy_bachelor'], sm.add_constant(df_iv[['trainings_completed']])).fit()
print(first_stage.summary())