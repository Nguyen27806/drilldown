import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Education & Career Success Dashboard",
    layout="wide"
)

@st.cache_data
def load_data():
    return pd.read_excel("education_career_success.xlsx", sheet_name=0)

df = load_data()

# -----------------------------
# SHARED ENTREPRENEURSHIP FILTER
# -----------------------------
st.sidebar.title("Filters")
statuses = ['Yes', 'No']
selected_statuses = st.sidebar.multiselect("Entrepreneurship", statuses, default=statuses)

# ==================================
# SECTION 1: BAR CHART (By Job Level & Age)
# ==================================

df_grouped = df[df['Entrepreneurship'].isin(selected_statuses)]
df_grouped = df_grouped.groupby(['Current_Job_Level', 'Age', 'Entrepreneurship']).size().reset_index(name='Count')
df_grouped['Percentage'] = df_grouped.groupby(['Current_Job_Level', 'Age'])['Count'].transform(lambda x: x / x.sum())

# Sidebar filters specific to bar chart
job_levels = sorted(df_grouped['Current_Job_Level'].unique())
selected_levels = st.sidebar.multiselect("Job Levels", job_levels, default=job_levels)

ages = sorted(df_grouped['Age'].unique())
ages_all = ['ALL'] + [str(a) for a in ages]
selected_ages = st.sidebar.multiselect("Ages", ages_all, default=['ALL'])

mode = st.sidebar.radio("Show as:", ["Percentage (%)", "Count"])

# Filtering
if 'ALL' in selected_ages:
    filtered = df_grouped[
        df_grouped['Current_Job_Level'].isin(selected_levels)
    ]
else:
    selected_ages_int = [int(a) for a in selected_ages]
    filtered = df_grouped[
        df_grouped['Current_Job_Level'].isin(selected_levels) &
        df_grouped['Age'].isin(selected_ages_int)
    ]

filtered = filtered[filtered['Entrepreneurship'].isin(selected_statuses)]

# Plotting
st.title("🚀 Education & Career Success Dashboard")

cols = st.columns(2)

if mode == "Percentage (%)":
    y_col = 'Percentage'
    fmt = lambda x: f"{x:.0%}"
    y_axis_title = "Percentage"
    y_tick_format = ".0%"
else:
    y_col = 'Count'
    fmt = lambda x: str(x)
    y_axis_title = "Count"
    y_tick_format = None

colors = {'Yes': '#FFD700', 'No': '#004080'}
order_levels = ['Entry', 'Executive', 'Mid', 'Senior']
levels_to_show = [lvl for lvl in order_levels if lvl in selected_levels]

for i, lvl in enumerate(levels_to_show):
    data_lvl = filtered[filtered['Current_Job_Level'] == lvl]
    if data_lvl.empty:
        with cols[i % 2]:
            st.write(f"### {lvl} — No data")
        continue

    fig = px.bar(
        data_lvl,
        x='Age',
        y=y_col,
        color='Entrepreneurship',
        barmode='stack',
        color_discrete_map=colors,
        category_orders={'Entrepreneurship': ['No', 'Yes'], 'Age': sorted(data_lvl['Age'].unique())},
        text=data_lvl[y_col].apply(fmt),
        labels={'Age': 'Age', y_col: y_axis_title},
        height=400,
        width=500,
        title=f"{lvl} Level"
    )

    fig.update_traces(textposition='inside')
    fig.update_layout(
        margin=dict(t=40, l=40, r=40, b=40),
        legend_title_text='Entrepreneurship',
        xaxis_tickangle=90
    )

    fig.update_yaxes(title=y_axis_title)
    if y_tick_format:
        fig.update_yaxes(tickformat=y_tick_format)

    with cols[i % 2]:
        st.plotly_chart(fig, use_container_width=True)

# ==================================
# SECTION 2: SUNBURST CHART
# ==================================

st.title("🌞 Career Path Sunburst")

# Apply shared Entrepreneurship filter
df_sunburst = df[df['Entrepreneurship'].isin(selected_statuses)]

def categorize_salary(salary):
    if salary < 30000:
        return '<30K'
    elif salary < 50000:
        return '30K–50K'
    elif salary < 70000:
        return '50K–70K'
    else:
        return '70K+'

df_sunburst['Salary_Group'] = df_sunburst['Starting_Salary'].apply(categorize_salary)

sunburst_data = df_sunburst.groupby(['Entrepreneurship', 'Field_of_Study', 'Salary_Group']).size().reset_index(name='Count')
total_count = sunburst_data['Count'].sum()
sunburst_data['Percentage'] = (sunburst_data['Count'] / total_count * 100).round(2)

ent_totals = sunburst_data.groupby('Entrepreneurship')['Count'].sum()
sunburst_data['Ent_Label'] = sunburst_data['Entrepreneurship'].map(
    lambda x: f"{x}<br>{round(ent_totals[x] / total_count * 100, 2)}%"
)

field_totals = sunburst_data.groupby(['Entrepreneurship', 'Field_of_Study'])['Count'].sum()
sunburst_data['Field_Label'] = sunburst_data.apply(
    lambda row: f"{row['Field_of_Study']}<br>{round(field_totals[(row['Entrepreneurship'], row['Field_of_Study'])] / total_count * 100, 2)}%",
    axis=1
)

sunburst_data['Salary_Label'] = sunburst_data['Salary_Group'] + '<br>' + sunburst_data['Percentage'].astype(str) + '%'
sunburst_data['Ent_Field'] = sunburst_data['Entrepreneurship'] + " - " + sunburst_data['Field_of_Study']

# Color maps
yes_colors = {
    'Engineering': '#aedea7', 'Business': '#dbf1d5', 'Arts': '#0c7734',
    'Computer Science': '#73c375', 'Medicine': '#00441b', 'Law': '#f7fcf5', 'Mathematics': '#37a055'
}
no_colors = {
    'Engineering': '#005b96', 'Business': '#03396c', 'Arts': '#009ac7',
    'Computer Science': '#8ed2ed', 'Medicine': '#b3cde0', 'Law': '#5dc4e1', 'Mathematics': '#0a70a9'
}

color_map = {}
for field, color in yes_colors.items():
    color_map[f"Yes - {field}"] = color
for field, color in no_colors.items():
    color_map[f"No - {field}"] = color
color_map['Yes'] = '#ffd16a'
color_map['No'] = '#ffd16a'

# Plot sunburst
fig = px.sunburst(
    sunburst_data,
    path=['Ent_Label', 'Field_Label', 'Salary_Label'],
    values='Count',
    color='Ent_Field',
    color_discrete_map=color_map,
    custom_data=['Percentage'],
    title='Career Path Insights: Education, Salary & Entrepreneurship'
)

fig.update_traces(
    insidetextorientation='radial',
    maxdepth=2,
    branchvalues="total",
    textinfo='label+text',
    hovertemplate="<b>%{label}</b><br>Value: %{value}<br>"
)

fig.update_layout(
    width=500,
    height=500,
    margin=dict(t=50, l=0, r=0, b=0)
)

col1, col2 = st.columns([3, 1])
with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 💡 How to use")
    st.markdown("""
- The chart displays three levels:  
    - *Entrepreneurship* (inner ring)  
    - *Field of Study* (middle ring)  
    - *Salary Group* (outer ring)  
- All segments include their percentage share.  
- Click a segment to zoom in and explore.
    """)
