import random
from datetime import datetime, timedelta

import mlflow
import pandas as pd
from fastapi import FastAPI
from mlflow.tracking import MlflowClient
from pydantic import BaseModel

app = FastAPI()


MODELS = {}


def fill_model_cache():
    client = MlflowClient()
    models = ["BikePoints_10"]
    for model_name in models:
        try:
            model_version = client.get_model_version_by_alias(f"{model_name}__prophet_model", "champion")
            model = mlflow.prophet.load_model(f"models:/{model_name}__prophet_model@champion")
            MODELS[model_name] = (model_version, model)
            print(f"Model {model_name} loaded successfully")
        except Exception as e:
            print(f"Error retrieving model {model_name} {e}")
            pass


@app.get("/predictions/")
async def get_predictions(place_id: str, time: str):
    # Parse time from ISO 8601 format, and this format "2024-07-06T17:22:21.191Z"
    parsed_time = datetime.fromisoformat(time.removesuffix("Z"))

    if place_id not in MODELS:
        print(f"Model for {place_id} not found, defaulting to existing models")
        model_version, model = MODELS["BikePoints_10"]
    else:
        model_version, model = MODELS[place_id]

    # move `parsed_time`  to the nearest 15 minute interval
    parsed_time = parsed_time - timedelta(minutes=parsed_time.minute % 15, seconds=parsed_time.second)

    generated_steps = 4 * 24

    dates = [
        (parsed_time + timedelta(minutes=15 * idx)).strftime("%Y-%m-%d %H:%M:%S") for idx in range(generated_steps)
    ]

    data_to_predict = pd.DataFrame(dates, columns=["ds"])

    forecast = model.predict(data_to_predict)

    # model.mak

    return {
        "place_id": place_id,
        "model_info": {
            "version": model_version.version,
            "name": model_version.name,
            "run_id": model_version.run_id,
            "artifact_uri": model_version.source,
        },
        "predictions": [
            {
                "time": row["ds"],
                "occupancy_ratio": row["yhat"],
                "occupancy_ratio_lower": row["yhat_lower"],
                "occupancy_ratio_upper": row["yhat_upper"],
            }
            for idx, row in forecast.iterrows()
        ],
    }


@app.get("/refresh_models/")
async def refresh_models():
    fill_model_cache()
    return {"status": "success"}


fill_model_cache()
