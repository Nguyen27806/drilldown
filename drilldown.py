import pandas as pd

# Load data from the Excel file
file_path = '/mnt/data/education_career_success.xlsx'
df = pd.read_excel(file_path, sheet_name='education_career_success')

# Define hierarchy and relevant columns
levels = ['Current_Job_Level', 'Field_of_Study', 'Gender']  # bottom to top
value_column = 'Job_Offers'
color_columns = ['Soft_Skills_Score', 'Networking_Score']

# Build hierarchical DataFrame function
def build_hierarchical_dataframe(df, levels, value_column, color_columns=None):
    df_list = []
    for i, level in enumerate(levels):
        df_tree = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
        dfg = df.groupby(levels[i:]).sum(numeric_only=True).reset_index()
        df_tree['id'] = dfg[level].copy()
        df_tree['parent'] = dfg[levels[i + 1]].copy() if i < len(levels) - 1 else 'total'
        df_tree['value'] = dfg[value_column]
        df_tree['color'] = dfg[color_columns[0]] / dfg[color_columns[1]]
        df_list.append(df_tree)
    total = pd.Series(dict(
        id='total',
        parent='',
        value=df[value_column].sum(),
        color=df[color_columns[0]].sum() / df[color_columns[1]].sum()
    ), name=0)
    df_list.append(total)
    df_all_trees = pd.concat(df_list, ignore_index=True)
    return df_all_trees

# Apply transformation
df_all_trees = build_hierarchical_dataframe(df, levels, value_column, color_columns)
average_score = df[color_columns[0]].sum() / df[color_columns[1]].sum()

# Save transformed data to use in plotting
df_all_trees_path = "/mnt/data/sunburst_transformed_data.csv"
df_all_trees.to_csv(df_all_trees_path, index=False)

df_all_trees_path
