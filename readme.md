# London Cycle Hire Scheme Prediction


## Run locally

Create a Python virtual environment and install the dependencies in `model/requirements.txt`:

```bash
pip install -r model/requirements.txt
```

Create a docker network:

```
docker network create shared_network
```

Start the **training** infrastructure with:

```bash
docker compose --env-file training.env -f training.docker-compose.yml up
```

Start the **serving** infrastructure with:

```bash
docker compose -f serving.docker-compose.yml up
```

Create an index pattern in Elastic:

```bash
python monitoring/create_index_pattern.py
```

Kickstart the training workflow with:

```bash
./training.sh
```

Relevant urls:

 - Frontend [http://localhost:5002/](http://localhost:5002/)
 - Prediction service [http://localhost:5001/](http://localhost:5001/)
 - Elastic [http://localhost:5601/](http://localhost:5601/)
