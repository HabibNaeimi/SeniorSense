import pandas as pd
import joblib

# Load the trained model from disk
model_path = r'G:\work\ICT-Turin\Programming for IOT\Codes\trained_model.pkl'
model = joblib.load(model_path)
print(f"Model loaded from {model_path}")

# Prediction function
def predict_state(temperature, heart_rate, blood_oxygen):
    input_data = pd.DataFrame([[temperature, heart_rate, blood_oxygen]], columns=['temperature', 'heart_rate', 'blood_oxygen'])
    state = model.predict(input_data)[0]
    return state

# Example prediction
example_temperature = 36.5
example_heart_rate = 75
example_blood_oxygen = 97

predicted_state = predict_state(example_temperature, example_heart_rate, example_blood_oxygen)
print(f"Predicted State: {predicted_state}")
