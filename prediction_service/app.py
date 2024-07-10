import logging
import os
import random
import sys
from datetime import datetime, timedelta
from uuid import uuid4

import logstash
import mlflow
import pandas as pd
from fastapi import FastAPI
from mlflow.tracking import MlflowClient
from pydantic import BaseModel

app = FastAPI()


MODELS = {}

# Get Logstash host and port from environment variables
LOGSTASH_HOST = os.environ.get("LOGSTASH_HOST", "localhost")
LOGSTASH_PORT = int(os.environ.get("LOGSTASH_PORT", 5000))

# Create logger
logger = logging.getLogger("python-logstash-logger")
logger.setLevel(logging.INFO)

# Create Logstash handler
logstash_handler = logstash.TCPLogstashHandler(LOGSTASH_HOST, LOGSTASH_PORT, version=1)

# Add Logstash handler to logger
logger.addHandler(logstash_handler)

# Add stdout handler to logger
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)


def fill_model_cache():
    client = MlflowClient()
    registered_models = client.search_registered_models(
        filter_string="tags.cycle_prediction='true'",
    )

    for registered_model in registered_models:
        try:
            model_version = client.get_model_version_by_alias(registered_model.name, "champion")
            model = mlflow.prophet.load_model(f"models:/{registered_model.name}@champion")
            model_name, *_ = registered_model.name.split("__")
            MODELS[model_name] = (model_version, model)
            logger.info("model loaded successfully", extra={"model": model_version.name})
        except Exception as e:
            logger.error("model failed to load", extra={"model": registered_model.name, "error": str(e)})


@app.get("/predictions/")
async def get_predictions(place_id: str, time: str, horizon: int = 20):
    # Parse time from ISO 8601 format, and this format "2024-07-06T17:22:21.191Z"
    parsed_time = datetime.fromisoformat(time.removesuffix("Z"))

    request_id = str(uuid4())

    if place_id not in MODELS:
        logger.warning("model not found", extra={"place_id": place_id})
        model_version, model = random.choice(list(MODELS.values()))
    else:
        model_version, model = MODELS[place_id]

    # move `parsed_time`  to the nearest 15 minute interval
    parsed_time = parsed_time - timedelta(minutes=parsed_time.minute % 15, seconds=parsed_time.second)

    dates = [(parsed_time + timedelta(minutes=15 * idx)).strftime("%Y-%m-%d %H:%M:%S") for idx in range(horizon)]

    data_to_predict = pd.DataFrame(dates, columns=["ds"])

    forecast = model.predict(data_to_predict)

    predictions = [
        {
            "order": idx,
            "time": row["ds"],
            "occupancy_ratio": row["yhat"],
            "occupancy_ratio_lower": row["yhat_lower"],
            "occupancy_ratio_upper": row["yhat_upper"],
        }
        for idx, row in forecast.iterrows()
    ]

    model_info = {
        "version": model_version.version,
        "name": model_version.name,
        "run_id": model_version.run_id,
        "artifact_uri": model_version.source,
    }

    request_info = {
        "request_id": request_id,
        "place_id": place_id,
        "requested_time": time,
        "served_time": parsed_time.isoformat(),
        "timestamp": datetime.now().isoformat(),
        "horizon": horizon,
    }

    logger.info("Prediction made", extra={"request": request_info, "model": model_info, "predictions": predictions})

    return {
        "model": model_info,
        "predictions": predictions,
        "request": request_info,
    }


@app.get("/refresh_models/")
async def refresh_models():
    fill_model_cache()
    return {"status": "success"}


fill_model_cache()
