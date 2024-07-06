import random
from datetime import datetime, timedelta

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Prediction(BaseModel):
    place_id: str
    time: str
    prediction: float


@app.get("/predictions/")
async def get_predictions(place_id: str, time: str):
    # Parse time from ISO 8601 format, and this format "2024-07-06T17:22:21.191Z"
    parsed_time = datetime.fromisoformat(time.removesuffix("Z"))

    return {
        "place_id": place_id,
        "predictions": [
            {
                "time": (parsed_time + timedelta(minutes=15 * idx)).isoformat(),
                "occupancy_ratio": random.random(),
            }
            for idx in range(4 * 24)
        ],
    }


@app.post("/predictions/")
async def insert_prediction(prediction: Prediction):
    return {
        "place_id": prediction.place_id,
        "time": prediction.time,
        "prediction": prediction.prediction,
        "message": "Prediction inserted",
    }
