# London Cycle Hire Scheme Prediction


## Run locally

### Requirements

 - [Docker](https://www.docker.com/)
 - [act](https://github.com/nektos/act) - Run your GitHub Actions locally 🚀

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

Kickstart the training using `act` to simulate GitHub Actions with:

```bash
act --container-architecture linux/amd64 --env-file actions.env
```

Or using the the local training workflow with:

```bash
./model/training.sh
```

Relevant urls:

 - Frontend [http://localhost:5002/](http://localhost:5002/)
 - Prediction service [http://localhost:5001/](http://localhost:5001/)
 - Elastic [http://localhost:5601/](http://localhost:5601/)
