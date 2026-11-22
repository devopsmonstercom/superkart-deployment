# Importing the necessary libraries
import joblib                                   # to load the serialized model
import pandas as pd                             # to convert the input data into a DataFrame
from flask import Flask, request, jsonify       # to create the API and handle requests/responses

# Initializing the Flask app
superkart_api = Flask("SuperKart Sales Forecast API")
superkart_api.json.sort_keys = False  # keep the batch output in row order

# Loading the trained model pipeline (preprocessing + Tuned Random Forest)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the order used during training
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type", "Product_Id_char",
    "Store_Age_Years", "Product_Type_Category",
]


# Home route to check that the API is running
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Forecast API!"


# Endpoint for online (single) prediction
@superkart_api.post("/v1/predict")
def predict_sales():
    # Reading the JSON payload sent in the request
    data = request.get_json()

    # Checking that all required features are present
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Converting the input into a single-row DataFrame with the expected columns
    input_df = pd.DataFrame([{f: data[f] for f in FEATURES}])

    # Making the prediction and returning it as JSON
    prediction = model.predict(input_df)[0]
    return jsonify({"Predicted_Product_Store_Sales_Total": round(float(prediction), 2)})


# Endpoint for batch prediction from an uploaded CSV file
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    # Reading the uploaded CSV file into a DataFrame
    file = request.files["file"]
    input_df = pd.read_csv(file)

    # Checking that all required features are present
    missing = [f for f in FEATURES if f not in input_df.columns]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Making predictions for all rows
    predictions = model.predict(input_df[FEATURES])

    # Returning a dictionary of {row index: predicted sales}
    output = {str(i): round(float(p), 2) for i, p in enumerate(predictions)}
    return jsonify(output)


# Running the app locally (inside Docker, gunicorn is used instead)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
