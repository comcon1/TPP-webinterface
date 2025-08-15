from fastapi.testclient import TestClient
from tppapi.tppapi import app  # import your FastAPI app
import tppapi.celery_tasks as ct
import time

client = TestClient(app)

mol_data = {
    'C2H2_nonrenum': 
"""COMPND    UNNAMED
HETATM    1  C   UNL     1       0.931   0.039  -0.043  1.00  0.00           C  
HETATM    2  C   UNL     1       2.266   0.039  -0.043  1.00  0.00           C  
HETATM    3  H   UNL     1       0.371   0.427   0.802  1.00  0.00           H  
HETATM    4  H   UNL     1       0.371  -0.349  -0.888  1.00  0.00           H  
HETATM    5  H   UNL     1       2.826   0.427   0.802  1.00  0.00           H  
HETATM    6  H   UNL     1       2.826  -0.349  -0.888  1.00  0.00           H  
END"""
}

def test_read_main():
    response = client.get("/")
    assert response.status_code == 404

def test_tpprenum_nonpdb():
    file_content = b"Hello World"
    files = {"file": ("hello.txt", file_content, "text/plain")}

    response = client.post("/process_tpprenum/", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["output_pdb"] is None
    assert "Can't read file format" in json_data["stdout"]


def test_tpprenum_pdb():
    files = {"file": (
        "hello.pdb", 
        mol_data["C2H2_nonrenum"], 
        "text/plain")
             }
    response = client.post("/process_tpprenum/", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["output_pdb"] is not None
    assert len(json_data["output_pdb"].strip().split('\n')) == 8
    assert "ERROR:" not in json_data["stdout"]


def test_requesting_status():
    task = ct.app.send_task(
        "tppapi.celery_tasks.moking_task_sleep", 
        args=[5])
    task_id = task.id

    # check pending
    time.sleep(3)
    response = client.get(f"/status/{task_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["task_id"] == task_id
    assert json_data["status"] == "PENDING"
    
    # check finished
    time.sleep(3)
    response = client.get(f"/status/{task_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["task_id"] == task_id
    assert json_data["status"] == "SUCCESS"
    assert json_data["result"] == 6


def test_diralive():
    # notask behavior
    response = client.get("/diralive/task-which-doesnot-exist")
    assert response.status_code == 404

    # moking-task with creation of a directory
    task = ct.app.send_task(
        "tppapi.celery_tasks.moking_task_sleep", 
        args=[4, True])
    task_id = task.id
    
    # task is still running
    time.sleep(1)
    response = client.get(f"/status/diralive/{task_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["task_id"] == task_id
    assert float(json_data["dir_alive"]) == -1 # means it still running

    time.sleep(5)
    response = client.get(f"/status/diralive/{task_id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["task_id"] == task_id
    da = float(json_data["dir_alive"])
    assert da > 4 and da < 5 # means it finished and counting

