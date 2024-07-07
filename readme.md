# London Cycle Hire Scheme Prediction


## Run locally

Start the **training** infrastructure with:

```bash
docker compose --env-file training.env -f training.docker-compose.yml up
```

Kickstart the training workflow with:

```bash
act --container-architecture linux/amd64 --env-file actions.env
```
