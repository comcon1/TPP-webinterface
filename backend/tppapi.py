"""
FastAPI back-end for TPPRENUM / TPPMKTOP runners.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
