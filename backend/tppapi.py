"""
FastAPI back-end for TPPRENUM / TPPMKTOP runners.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
import celery_tasks as ct

app = FastAPI()

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Or specify ["http://address:port"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )


@app.post("/process_tpprenum/")
async def process_tpprenum(file: UploadFile = File(...)):
    """Process a PDB file using TPPRENUM.
    This endpoint accepts a PDB file, processes it with TPPRENUM
    in a sequential mode

    :param file: uploaded file, defaults to File(...)
    :raises HTTPException: if task fails or timeout occurs
    :return: JSON response with output PDB and stdout
    """
    # Read file content
    pdbtxt = await file.read()
    pdbtxt = pdbtxt.decode()  # assuming the file is text

    # Submit task to Celery
    task = ct.request_process_tpprenum.delay(pdbtxt)
    try:
        # Wait for result (optionally set a timeout)
        output_pdb, stdout = task.get(timeout=60)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task failed: {e}")

    return {"output_pdb": output_pdb, "stdout": stdout}


@app.post("/queue_tpprenum/")
async def queue_tpprenum(file: UploadFile = File(...)):
    # Save file, process, or pass file info to Celery
    pdbtxt = await file.read()
    pdbtxt = pdbtxt.decode()  # assuming the file is text
    # Start Celery task
    task = ct.app.send_task("celery_tasks.request_process_tpprenum", 
                            args=[pdbtxt])
    return {"task_id": task.id}


@app.post("/queue_tppmktop/")
async def queue_tppmktop(file: UploadFile = File(...)):
    """Queue a TPPMKTOP task with the uploaded file."""
    pdbtxt = await file.read()
    pdbtxt = pdbtxt.decode()  # assuming the file is text
    # Start Celery task
    task = ct.app.send_task("celery_tasks.request_process_tppmktop", 
                            args=[pdbtxt])
    return {"task_id": task.id}


@app.get("/status/{task_id}")
def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=ct.app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": (
            task_result.result
            if task_result.status == "SUCCESS"
            else None
            )
    }


