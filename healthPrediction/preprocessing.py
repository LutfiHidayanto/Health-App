from sklearn.preprocessing import StandardScaler
from django.conf import settings 
import pickle
import pandas as pd


features = ['Diabetes_binary', 'HighBP', 'HighChol', 'CholCheck', 'Smoker',
       'Stroke', 'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
       'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'DiffWalk', 'Sex',
       'BMI', 'GenHlth', 'MentHlth', 'PhysHlth', 'Age']

categorical_features = ['Diabetes_binary', 'HighBP', 'HighChol', 'CholCheck', 'Smoker', 'Stroke', 'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'DiffWalk', 'Sex']
numerical_features = ['BMI', 'GenHlth', 'MentHlth', 'PhysHlth', 'Age']

def convertFormData(form):
    data_dict = {}
    for name, value in form:
        data_dict[name] = [value]
    data_dict = pd.DataFrame(data_dict)

    return data_dict        
def scaleData(data):
    try:
        scaler = StandardScaler()
        data[numerical_features] = scaler.fit_transform(data[numerical_features])
    except Exception as e:
        print(f"Exception: {e}")
        return None
    return data

def predict(data, model):
    try:
        prediction = model.predict(data)
    except Exception as e:
        print(f"Exception: {e}")
        return None
    return prediction
    

def loadModel(modelPath):
    try:
        with open(modelPath, 'rb') as f:
            model = pickle.load(f)
    except Exception as e:
        print(f"Exception: {e}")
        return None
    return model