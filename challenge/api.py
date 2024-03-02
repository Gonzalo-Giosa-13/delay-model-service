from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError, validator
from typing import List
from joblib import load
import pandas as pd
from typing import List, Optional

app = FastAPI()

# Asegúrate de que la ruta al modelo sea accesible desde la ubicación donde se ejecuta la API
model_filename = 'reg_model_2.joblib'
model = load(model_filename)

class FlightData(BaseModel):
    OPERA: str
    MES: int
    TIPOVUELO: str
    # Campos opcionales en caso de que no los uses en el modelo
    SIGLADES: Optional[str] = None
    DIANOM: Optional[str] = None

    @validator('MES')
    def check_mes(cls, v):
        if v < 1 or v > 12:
            raise ValueError('MES must be between 1 and 12')
        return v

    @validator('TIPOVUELO')
    def check_tipo_vuelo(cls, v):
        if v not in ['I', 'N']:
            raise ValueError('TIPOVUELO must be I or N')
        return v

class PredictRequest(BaseModel):
    flights: List[FlightData]

@app.post("/predict/")
def predict(request: PredictRequest):
    try:
        flights_data = [flight.dict(exclude_none=True) for flight in request.flights]
        df = pd.DataFrame(flights_data)

        data_transformed = transform_data(df)

        prediction = model.predict(data_transformed)
        # Cambio para asegurarse de devolver el formato esperado en las pruebas
        return {"predict": prediction.tolist()}
    except ValidationError as e:
        # Este bloque captura errores de validación de Pydantic
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        # Este bloque captura otros errores, puedes ajustar el manejo según tus necesidades
        raise HTTPException(status_code=400, detail=str(e))

def transform_data(df):
    # Asumiendo que esta función prepara los datos correctamente para el modelo
    data_transformed = pd.concat([
        pd.get_dummies(df['OPERA'], prefix='OPERA'),
        pd.get_dummies(df['MES'], prefix='MES'),
        pd.get_dummies(df['TIPOVUELO'], prefix='TIPOVUELO'),
    ], axis=1, sort=False)

    # Asegurarse de que todas las columnas esperadas estén presentes
    expected_columns = model.feature_names_in_
    missing_cols = set(expected_columns) - set(data_transformed.columns)
    for col in missing_cols:
        data_transformed[col] = 0
    data_transformed = data_transformed[expected_columns]
    
    return data_transformed
