from celery import shared_task


@shared_task(bind=True, name="app.worker.tasks.ingest_dataset")
def ingest_dataset(self, dataset_id: str) -> dict:
    return {"dataset_id": dataset_id, "status": "queued"}


@shared_task(bind=True, name="app.worker.tasks.generate_embeddings")
def generate_embeddings(self, dataset_id: str) -> dict:
    return {"dataset_id": dataset_id, "status": "queued"}
