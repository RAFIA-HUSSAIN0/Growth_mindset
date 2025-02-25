import streamlit as st
import pandas as pd
import os
from io import BytesIO
import matplotlib.pyplot as plt

# Set up the app
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Custom CSS for Better UI/UX
st.markdown("""
    <style>
    body {
        background-color: #0d1117;
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        background-color: #0d1117;
    }
    .sidebar .sidebar-content {
        background-color: #161b22;
    }
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 5px;
        font-size: 16px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #2ea043;
    }
    .stDownloadButton>button {
        background-color: #8250df;
        color: white;
        border-radius: 5px;
        font-size: 16px;
        padding: 10px;
    }
    .stDownloadButton>button:hover {
        background-color: #7b3fdb;
    }
    .stFileUploader label {
        font-size: 18px;
        font-weight: bold;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for Navigation
st.sidebar.title("⚙️ Data Sweeper")
st.sidebar.write("Upload, clean, and visualize your data efficiently.")

# File uploader without arrow
uploaded_files = st.sidebar.file_uploader("📂 Upload CSV or Excel", type=["csv", "xlsx"], accept_multiple_files=True, label_visibility='collapsed')

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.sidebar.error(f"❌ Unsupported file type: {file_ext}")
            continue
        
        # Display Data Preview
        st.subheader(f"📊 Preview: {file.name}")
        st.dataframe(df.head(10))
        
        # Data Cleaning Options
        st.subheader("🧹 Data Cleaning")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🗑 Remove Duplicates - {file.name}"):
                df.drop_duplicates(inplace=True)
                st.success("✔ Duplicates removed successfully!")
        
        with col2:
            if st.button(f"🔄 Fill Missing Values - {file.name}"):
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.success("✔ Missing values filled with column mean!")
        
        # Data Sorting
        st.subheader("🔃 Sort Data")
        sort_column = st.selectbox(f"Select column to sort - {file.name}", df.columns, index=0)
        sort_order = st.radio("Sort Order", ["Ascending", "Descending"], horizontal=True)
        df = df.sort_values(by=sort_column, ascending=(sort_order == "Ascending"))
        
        # Data Summary
        st.subheader("📊 Data Summary")
        st.write(df.describe())
        
        # Column Selection
        st.subheader("🎯 Select Columns")
        columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]
        
        # Data Search and Filter
        st.subheader("🔍 Search Data")
        search_query = st.text_input(f"Search in {file.name}")
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
        
        # Data Visualization
        st.subheader("📈 Data Visualization")
        viz_options = ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot", "Histogram"]
        viz_choice = st.selectbox(f"Choose visualization for {file.name}", viz_options)
        
        if viz_choice == "Bar Chart":
            st.bar_chart(df.select_dtypes(include='number'))
        elif viz_choice == "Line Chart":
            st.line_chart(df.select_dtypes(include='number'))
        elif viz_choice == "Pie Chart":
            if len(df.select_dtypes(include='number').columns) > 0:
                col_to_plot = st.selectbox("Select column for Pie Chart", df.select_dtypes(include='number').columns)
                fig, ax = plt.subplots()
                df[col_to_plot].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
                ax.set_ylabel("")
                st.pyplot(fig)
            else:
                st.warning("⚠ No numeric columns available for pie chart.")
        elif viz_choice == "Scatter Plot":
            if len(df.select_dtypes(include='number').columns) > 1:
                col_x = st.selectbox("Select X-axis column", df.select_dtypes(include='number').columns)
                col_y = st.selectbox("Select Y-axis column", df.select_dtypes(include='number').columns)
                fig, ax = plt.subplots()
                ax.scatter(df[col_x], df[col_y])
                ax.set_xlabel(col_x)
                ax.set_ylabel(col_y)
                st.pyplot(fig)
            else:
                st.warning("⚠ Not enough numeric columns for scatter plot.")
        elif viz_choice == "Histogram":
            num_col = st.selectbox("Select column for Histogram", df.select_dtypes(include='number').columns)
            fig, ax = plt.subplots()
            df[num_col].hist(ax=ax, bins=20)
            st.pyplot(fig)
        
        # Conversion Options
        st.subheader("💾 Download Processed Data")
        conversion_type = st.radio(f"Convert {file.name} to:", ("CSV", "Excel"), key=file.name)
        
        if conversion_type == "CSV":
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, file_name=f"{file.name}_processed.csv", mime="text/csv")
        elif conversion_type == "Excel":
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            processed_data = output.getvalue()
            st.download_button("⬇️ Download Excel", processed_data, file_name=f"{file.name}_processed.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
