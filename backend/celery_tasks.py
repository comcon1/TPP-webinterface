"""_summary_
This module contains the tasks for the Cellery project.
"""

from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
import subprocess
import re
import os
import shutil
import time

# Configure Celery to use Redis broker and backend
app = Celery('tasks')
app.config_from_object('celeryconfig')


@app.task(bind=True)
def request_program_version(self, program_name):
    """Requests the version of an external program.

    :param program_name: which program you are requestion

    :return: Version string or error message
    """
    print(f"My task ID is: {self.request.id}")
    container_name = self.app.conf.get('CONTAINER_NAME', 'tpproject-tpp-1')
    logger = self.app.log.get_default_logger()
    logger.info("Requesting version for program: %s" % program_name)
    
    if program_name == 'tppmktop':
        pname = 'runtppmktop.sh'
    elif program_name == 'tpprenum':
        pname = 'tpprenum'
    else:
        logger.error(f"Unknown program name: {program_name}")
        return (None, None)
    
    try:
        # Run the external command and capture its output
        result = subprocess.run(
            ['docker', 'exec', container_name, pname, '-h'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Capture stderr too
            text=True,                 # Decode to string
            check=True                 # Raise CalledProcessError on nonzero exit
        )
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Error running command: {e.cmd}\n"
            f"Exit code: {e.returncode}\n"
            f"Output: {e.output}"
        )
        return (None, None)
    else:
        v0 = None
        v1 = None
        for ln in result.stdout.splitlines():
            m = re.match(r'\s*TPP version: (.+),\s*(.+)$', ln)
            if m:
                v0 = m.group(1)
                v1 = m.group(2)
                logger.info(
                    f"Found version: {v0}, {v1} for program: {program_name}"
                )
                return (v0, v1)
        logger.error(
            f"Could not find version information in output:\n{result.stdout}"
        )
        return (None, None)


@app.task(bind=True, soft_time_limit=60)
def request_process_tpprenum(self, pdb_content):
    """
    Process renum on PDB strings..
    """
    container_name = self.app.conf.get('CONTAINER_NAME', 'tpproject-tpp-1')
    container_vol = self.app.conf.get('CONTAINER_VOL', '/tmp/work')
    logger = self.app.log.get_default_logger()

    logger.info("Requested RENUM on file with %n strings")
    twd = os.path.join(container_vol, self.request.id)
    try:
        os.mkdir(twd)
    except Exception as e:
        logger.error(
                f'Problem making calc-folder {twd} '
                f'Exception: {e}')
        return None, str(e)
    logger.info(f"Saving PDB: {twd}/input.pdb")
    try:
        with open(os.path.join(twd, 'input.pdb'), 'w') as fd:
            fd.write(pdb_content)
    except Exception as e:
        logger.error(
                f'Problem making calc-PDB {twd}/input.pdb '
                f'Exception: {e}')
        return None,  str(e)

    logger.info("Saved.")
    
    try:
        # Run the external command and capture its output
        logger.info("Running TPPRENUM")
        rel_input = self.request.id + '/input.pdb'
        rel_output = self.request.id + '/output.pdb'
        procres = subprocess.run(
            ['docker', 'exec', container_name, 'tpprenum', 
             '-i', rel_input, '-o', rel_output],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Capture stderr too
            text=True,                 # Decode to string
            check=True                 # Raise CalledProcessError on nonzero exit
        )
        time.sleep(5)
        logger.info("TPPRENUM finished")
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Error running command: {e.cmd}\n"
            f"Exit code: {e.returncode}\n"
            f"Output: {e.output}"
        )
        return (None, e.output)
    except SoftTimeLimitExceeded:
        logger.warning(f"Task {self.request.id} hit soft time limit. Cleaning up.")
        result_pdb = None
    else:
        logger.info("Normal execution!")
        with open(os.path.join(twd, 'output.pdb'), 'r') as fd:
            pdb_out = fd.read()
        result_pdb = pdb_out
    finally:
        logger.info(f"Cleaning calc-folder {twd}..")
        shutil.rmtree(twd)
        return result_pdb, procres.stdout

