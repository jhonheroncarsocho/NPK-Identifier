import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Additional libraries for specific pre-processing techniques (optional)
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np

# for NN
import tensorflow as tf
from tensorflow import lite
import tflite_runtime.interpreter as tflite
import os
import random

# load csv files containing spectral data
data = pd.read_csv("./Training_Set - Copy.csv")
unkwown = pd.read_csv("./test_set - Copy.csv")

# Separate features (spectral data) and target variables (OM, P, K)
features = np.array(data.iloc[:, 4:].values)
target_OM = data["Organic Matter (OM), %"]
target_P = data["Phosphorus (P), ppm"]
target_K = data["Potassium [K], ppm"]

#unknown
unknown_features = np.array(unkwown.iloc[:, 4:].values)
unknown_OM = unkwown["Organic Matter (OM), %"]
unknown_P = unkwown["Phosphorus (P), ppm"]
unknown_K = unkwown["Potassium [K], ppm"]

# 0 = OM, 1 = P, 2 = K
target_what = 2
if target_what == 0:
  target_val = target_OM
  target_unk = unknown_OM
  var_name = "Organic Matter (OM), %"
  model_dir = "./OM_Opti/final_regression_model_OM.h5"
  convert_lite = "./final_regression_model_OM.tflite"
  FILTER_SIZE = 51
  L2_BETA = 0.006500000000000001

elif target_what == 1:
  target_val = target_P
  target_unk = unknown_P
  var_name = "Phosphorus (P), ppm"
  model_dir = "./P_Opti/final_regression_model_P.h5"
  convert_lite = "./final_regression_model_P.tflite"
  FILTER_SIZE = 17
  L2_BETA = 0.0205

else:
  target_val = target_K
  target_unk = unknown_K
  var_name = "Potassium [K], ppm"
  model_dir = "./K_Opti/final_regression_model_K.h5"
  convert_lite = "./final_regression_model_K.tflite"
  FILTER_SIZE = 9
  L2_BETA = 0.034


scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)
unknown_features = scaler.fit_transform(unknown_features)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features_scaled, target_val, test_size=0.2, random_state=42)


## Define random seeds ir order to maintain reproducible results through multiple testing phases
def reproducible_comp():
    os.environ['PYTHONHASHSEED'] = '0'
    np.random.seed(42)
    random.seed(42)
    tf.random.set_seed(42)


## Make computations reproducible
tf.keras.backend.clear_session()
reproducible_comp() 

# Convert H5 file model to tflite
model_cnn = tf.keras.models.load_model(model_dir)
converter = lite.TFLiteConverter.from_keras_model(model_cnn)
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Optional optimizations
tflite_model = converter.convert()

# Specify the desired filename for the TensorFlow Lite model
with open(convert_lite, "wb") as f:
    f.write(tflite_model)
    
tf.keras.backend.clear_session()

interpreter = tflite.Interpreter(model_path=convert_lite)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Sample input data
pred = []
for sample in unknown_features:
  input_data = sample.astype(np.float32).reshape(1, 128)
  interpreter.set_tensor(input_details[0]['index'], input_data)

  # Run inference
  interpreter.invoke()

  # Get output data
  output_data = interpreter.get_tensor(output_details[0]['index'])

  # Print output (modify as needed for your model's output format)
  pred.append(output_data)

# test unknown predection
print("Unknown")
mse = mean_squared_error(target_unk, pred)
r2 = r2_score(target_unk, pred)

print(f"Mean Squared Error: {mse}")
print(f"R-Squared: {r2}\n")

##plt.subplot(223)
plt.scatter(target_unk, pred)
plt.title(f"Unknown: {var_name}")
plt.xlabel("Actual Values")
plt.ylabel("Predicted Values")
plt.plot([min(target_unk), max(target_unk)], [min(target_unk), max(target_unk)], linestyle='--', color='black', linewidth=2)

plt.show()
