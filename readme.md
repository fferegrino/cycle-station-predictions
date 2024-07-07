# London Cycle Hire Scheme Prediction


## Run locally

Create a Python virtual environment and install the dependencies in `model/requirements.txt`:

```
docker network create shared_network
```

```bash
pip install -r model/requirements.txt
```

Start the **training** infrastructure with:

```bash
docker compose --env-file training.env -f training.docker-compose.yml up
```

Start the **serving** infrastructure with:

```bash
docker compose -f serving.docker-compose.yml up
```

Kickstart the training workflow with:

```bash
./training.sh
```
