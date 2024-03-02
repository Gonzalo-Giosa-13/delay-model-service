import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from datetime import datetime

class DelayModel:

    def __init__(self):
        self._model = None
        self.top_10_features = [
            "OPERA_Latin American Wings", 
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air"
        ]

    def preprocess(self, data: pd.DataFrame, target_column: str = None):
        data['period_day'] = data['Fecha-I'].apply(self.get_period_day)
        data['high_season'] = data['Fecha-I'].apply(self.is_high_season)
        data['min_diff'] = data.apply(self.get_min_diff, axis=1)
        data['delay'] = np.where(data['min_diff'] > 15, 1, 0)
        
        # Asegurar que las dummies sean generadas correctamente
        data = pd.get_dummies(data, columns=['OPERA', 'TIPOVUELO', 'MES'])
        features = data[[col for col in self.top_10_features if col in data.columns]].copy()

        for col in self.top_10_features:
            if col not in features.columns:
                features[col] = 0

        features = features[self.top_10_features] # Asegurar el orden correcto de las columnas

        if target_column:
            target = pd.DataFrame(data[target_column], columns=[target_column])
            return features, target
        return features

    def fit(self, features: pd.DataFrame, target: pd.DataFrame):
        self._model = LogisticRegression(class_weight='balanced')
        self._model.fit(features, target)

    def predict(self, features: pd.DataFrame):
        if self._model is None:
            raise RuntimeError("Model is not trained yet.")
        return self._model.predict(features).tolist()

    @staticmethod
    def get_period_day(date):
        date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').time()
        morning_min = datetime.strptime("05:00", '%H:%M').time()
        morning_max = datetime.strptime("11:59", '%H:%M').time()
        afternoon_min = datetime.strptime("12:00", '%H:%M').time()
        afternoon_max = datetime.strptime("18:59", '%H:%M').time()
        evening_min = datetime.strptime("19:00", '%H:%M').time()
        evening_max = datetime.strptime("23:59", '%H:%M').time()
        night_min = datetime.strptime("00:00", '%H:%M').time()
        night_max = datetime.strptime("4:59", '%H:%M').time()
        
        if morning_min < date_time <= morning_max:
            return 'mañana'
        elif afternoon_min < date_time <= afternoon_max:
            return 'tarde'
        elif evening_min < date_time <= evening_max or night_min <= date_time < night_max:
            return 'noche'
        else:
            return 'noche'  # Considerar el caso fuera de horas como 'noche'

    @staticmethod
    def is_high_season(fecha):
        fecha_año = int(fecha.split('-')[0])
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        range1_min = datetime.strptime(f'15-Dec-{fecha_año}', '%d-%b-%Y')
        range1_max = datetime.strptime(f'31-Dec-{fecha_año}', '%d-%b-%Y')
        range2_min = datetime.strptime(f'01-Jan-{fecha_año}', '%d-%b-%Y')
        range2_max = datetime.strptime(f'03-Mar-{fecha_año}', '%d-%b-%Y')
        range3_min = datetime.strptime(f'15-Jul-{fecha_año}', '%d-%b-%Y')
        range3_max = datetime.strptime(f'31-Jul-{fecha_año}', '%d-%b-%Y')
        range4_min = datetime.strptime(f'11-Sep-{fecha_año}', '%d-%b-%Y')
        range4_max = datetime.strptime(f'30-Sep-{fecha_año}', '%d-%b-%Y')
        
        if ((range1_min <= fecha <= range1_max) or 
            (range2_min <= fecha <= range2_max) or 
            (range3_min <= fecha <= range3_max) or
            (range4_min <= fecha <= range4_max)):
            return 1
        else:
            return 0

    @staticmethod
    def get_min_diff(row):
        fecha_o = datetime.strptime(row['Fecha-O'], '%Y-%m-%d %H:%M:%S')
        fecha_i = datetime.strptime(row['Fecha-I'], '%Y-%m-%d %H:%M:%S')
        min_diff = (fecha_o - fecha_i).total_seconds() / 60
        return min_diff
