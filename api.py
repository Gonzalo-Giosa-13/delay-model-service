from fastapi import FastAPI
from pydantic import BaseModel
from joblib import load
import pandas as pd

app = FastAPI()

# Cargar el modelo guardado
model_filename = '../challenge/reg_model_2.joblib'
model = load(model_filename)

class FlightData(BaseModel):
    OPERA: str
    MES: int
    TIPOVUELO: str
    SIGLADES: str = None  # Opcional, en caso de que no lo uses en el modelo
    DIANOM: str = None  # Opcional, en caso de que no lo uses en el modelo

@app.post("/predict/")
def predict(flight: FlightData):
    data = pd.DataFrame([flight.dict()])
    data_transformed = pd.concat([
        pd.get_dummies(data['OPERA'], prefix='OPERA'),
        pd.get_dummies(data['MES'], prefix='MES'),
        pd.get_dummies(data['TIPOVUELO'], prefix='TIPOVUELO')
    ], axis=1)

    # Asumimos que tienes una lista de todas las columnas esperadas por el modelo
    expected_columns = model.feature_names_in_  # Si tu versión de sklearn lo soporta
    # Si model.feature_names_in_ no está disponible, reemplázalo por una lista definida manualmente.

    # Asegurarse de que todas las columnas esperadas estén presentes en data_transformed
    for column in expected_columns:
        if column not in data_transformed.columns:
            data_transformed[column] = 0

    # Reordenar las columnas de data_transformed para que coincidan con el orden esperado por el modelo
    data_transformed = data_transformed[expected_columns]

    prediction = model.predict(data_transformed)
    return {"prediction": "Retrasado" if prediction[0] == 1 else "A tiempo"}


