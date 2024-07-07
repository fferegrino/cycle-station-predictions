import mlflow

mlflow.set_experiment("london-bike-sharing")
run = mlflow.start_run()
mlflow.end_run()
print(run.info.run_id)