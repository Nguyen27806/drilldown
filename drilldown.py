import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Sunburst Chart: Gender → Field → GPA → Career Satisfaction")

uploaded_file = st.file_uploader("Upload the Excel file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="education_career_success")

    # Group GPA
    def group_gpa(gpa):
        if gpa < 2.5:
            return "Low"
        elif gpa < 3.2:
            return "Medium"
        else:
            return "High"

    # Group Satisfaction
    def group_satisfaction(score):
        if score <= 3:
            return "Low"
        elif score <= 7:
            return "Medium"
        else:
            return "High"

    df["University_GPA_Group"] = df["University_GPA"].apply(group_gpa)
    df["Career_Satisfaction_Group"] = df["Career_Satisfaction"].apply(group_satisfaction)

    sunburst_data = df.groupby(["Gender", "Field_of_Study", "University_GPA_Group", "Career_Satisfaction_Group"]).size().reset_index(name="Count")

    fig = px.sunburst(
        sunburst_data,
        path=["Gender", "Field_of_Study", "University_GPA_Group", "Career_Satisfaction_Group"],
        values="Count",
        title="Gender → Field → GPA → Career Satisfaction",
    )

    st.plotly_chart(fig)
