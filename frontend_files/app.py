# Importing the necessary libraries
import os
import requests                 # to send requests to the backend API
import pandas as pd             # to handle the batch input/output data
import streamlit as st          # to build the interactive web UI

# URL of the backend Flask API
# Inside the Docker network, the backend container is reached by its container name
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

# Page configuration and title
st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

# Two tabs: one for a single prediction and one for batch predictions
tab_online, tab_batch = st.tabs(["Online Prediction", "Batch Prediction"])

# ---------------- Online (single) prediction ----------------
with tab_online:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, max_value=30.0, value=12.66, step=0.01)
        product_allocated_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0,
                                                 value=0.027, step=0.001, format="%.3f")
        product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=0.01)
    with col2:
        product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_id_char = st.selectbox("Product Family (Product_Id prefix)", ["FD", "DR", "NC"],
                                       help="FD = Food, DR = Drinks, NC = Non-Consumables")
        product_type_category = st.selectbox("Product Type Category", ["Non Perishables", "Perishables"])

    st.subheader("Store details")
    col3, col4 = st.columns(2)
    with col3:
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"], index=1)
        store_location_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
    with col4:
        store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2",
                                                 "Departmental Store", "Food Mart"], index=1)
        store_establishment_year = st.number_input("Store Establishment Year", min_value=1950, max_value=2025,
                                                   value=2009, step=1)

    # Building the payload in the format expected by the backend API
    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": product_sugar_content,
        "Product_Allocated_Area": product_allocated_area,
        "Product_MRP": product_mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": store_location_city_type,
        "Store_Type": store_type,
        "Product_Id_char": product_id_char,
        "Store_Age_Years": 2025 - int(store_establishment_year),  # same feature engineering as in training
        "Product_Type_Category": product_type_category,
    }

    if st.button("Predict Sales"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Predicted_Product_Store_Sales_Total"]
                st.success(f"Predicted Product Store Sales Total: {prediction:,.2f}")
            else:
                st.error(f"API error ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the backend API: {e}")

# ---------------- Batch prediction ----------------
with tab_batch:
    st.subheader("Upload a CSV file")
    st.write("The file must contain the 10 model features as columns.")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None and st.button("Predict Batch"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                                     files={"file": uploaded_file.getvalue()}, timeout=60)
            if response.status_code == 200:
                # Adding the predictions as a new column next to the input data
                result_df = pd.read_csv(uploaded_file)
                result_df["Predicted_Sales"] = list(response.json().values())
                st.success(f"Predictions generated for {len(result_df)} rows.")
                st.dataframe(result_df)
                st.download_button("Download predictions", result_df.to_csv(index=False),
                                   file_name="superkart_predictions.csv", mime="text/csv")
            else:
                st.error(f"API error ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the backend API: {e}")
