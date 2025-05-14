import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load raw data
df = pd.read_excel("education_career_success.xlsx", sheet_name="education_career_success")

# Define hierarchy and metrics
levels = ['Current_Job_Level', 'Field_of_Study', 'Gender']
value_column = 'Job_Offers'
color_columns = ['Soft_Skills_Score', 'Networking_Score']

# Build hierarchical dataframe
def build_hierarchical_dataframe(df, levels, value_column, color_columns=None):
    df_list = []
    for i, level in enumerate(levels):
        df_tree = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
        dfg = df.groupby(levels[i:]).sum(numeric_only=True).reset_index()
        df_tree['id'] = dfg[level]
        df_tree['parent'] = dfg[levels[i+1]] if i < len(levels) - 1 else 'total'
        df_tree['value'] = dfg[value_column]
        df_tree['color'] = dfg[color_columns[0]] / dfg[color_columns[1]]
        df_list.append(df_tree)

    # Add root
    total = pd.Series(dict(
        id='total',
        parent='',
        value=df[value_column].sum(),
        color=df[color_columns[0]].sum() / df[color_columns[1]].sum()
    ), name=0)
    df_all_trees = pd.concat(df_list + [total.to_frame().T], ignore_index=True)
    return df_all_trees

# Build tree
df_all_trees = build_hierarchical_dataframe(df, levels, value_column, color_columns)
average_score = df_all_trees["color"].mean()

# Make sunburst with 2 subplots
fig = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]])

# Full hierarchy
fig.add_trace(go.Sunburst(
    labels=df_all_trees['id'],
    parents=df_all_trees['parent'],
    values=df_all_trees['value'],
    branchvalues='total',
    marker=dict(
        colors=df_all_trees['color'],
        colorscale='RdBu',
        cmid=average_score
    ),
    hovertemplate='<b>%{label}</b><br>Job Offers: %{value}<br>Ratio: %{color:.2f}',
    name=''
), row=1, col=1)

# Limited depth version
fig.add_trace(go.Sunburst(
    labels=df_all_trees['id'],
    parents=df_all_trees['parent'],
    values=df_all_trees['value'],
    branchvalues='total',
    marker=dict(
        colors=df_all_trees['color'],
        colorscale='RdBu',
        cmid=average_score
    ),
    hovertemplate='<b>%{label}</b><br>Job Offers: %{value}<br>Ratio: %{color:.2f}',
    maxdepth=2
), row=1, col=2)

fig.update_layout(
    title_text="Sunburst Chart: Job Level → Field → Gender (Color = Soft Skills / Networking)",
    margin=dict(t=10, b=10, l=10, r=10)
)

fig.show()
