"""_summary_
This module contains the tasks for the Cellery project.
"""

from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
import subprocess
import re
import os
import time
import shutil

# Configure Celery to use Redis broker and backend
app = Celery('tpp')
app.config_from_object('tppapi.celeryconfig')


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
        os.rmdir(twd)
        return None,  str(e)

    logger.info("Saved.")
    result_pdb = None
    procres = None

    try:
        # Run the external command and capture its output
        logger.info("Running TPPRENUM")
        rel_input = self.request.id + '/input.pdb'
        rel_output = self.request.id + '/output.pdb'
        procres = subprocess.run(
            ['docker', 'exec',
             "--user", f"{os.getuid()}:{os.getgid()}",
             container_name, 'tpprenum',
             '-i', rel_input, '-o', rel_output],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Capture stderr too
            text=True,                 # Decode to string
            check=True,                # Raise CalledProcessError on nonzero exit
            timeout=60
        )
        logger.info("TPPRENUM finished")
    except subprocess.CalledProcessError as e:
        # show max last 50 
        lns = e.output.split('\n')
        if len(lns) > 50:
            lns = lns[-50:-1]
        # logging
        logger.error(
            f"Error running command: {e.cmd}\n"
            f"Exit code: {e.returncode}\n"
            "Output: " + '\n'.join(lns)
        )
        return (None, e.output)
    except SoftTimeLimitExceeded:
        logger.warning(f"Task {self.request.id} hit soft time limit. Cleaning up.")
        #TODO: timeout task termination
        return (None, "You upload too large PDB file and reach current timeout.")
    else:
        logger.info("Normal execution!")
        with open(os.path.join(twd, 'output.pdb'), 'r') as fd:
            pdb_out = fd.read()
        result_pdb = pdb_out
        return result_pdb, procres.stdout
    finally:
        logger.info(f"Cleaning calc-folder {twd}..")
        shutil.rmtree(twd)


@app.task(bind=True, soft_time_limit=60)
def request_process_tppmktop(self, pdb_content):
    """
    Process TPPMKTOP on PDB strings. Output folder will live 5 min after 
    result is made.

    :return: Tuple with status code and path to the output folder
             0 for success, 1 for error, 2 for exception
             if 0/1, the second element is the path to the output folder
             if 2, the second element is the error message
    """
    container_name = self.app.conf.get('CONTAINER_NAME', 'tpproject-tpp-1')
    container_vol = self.app.conf.get('CONTAINER_VOL', '/tmp/work')
    logger = self.app.log.get_default_logger()

    logger.info("Requested MKTOP on file with %n strings")
    twd = os.path.join(container_vol, self.request.id)
    try:
        os.mkdir(twd)
    except Exception as e:
        logger.error(
                f'Problem making calc-folder {twd} '
                f'Exception: {e}')
        return (2, str(e))
    logger.info(f"Saving PDB: {twd}/input.pdb")
    try:
        with open(os.path.join(twd, 'input.pdb'), 'w') as fd:
            fd.write(pdb_content)
    except Exception as e:
        logger.error(
                f'Problem making calc-PDB {twd}/input.pdb '
                f'Exception: {e}')
        return (2,  str(e))

    logger.info("Saved.")
    
    try:
        # Run the external command and capture its output
        logger.info("Running TPPMKTOP")
        rel_input = self.request.id + '/input.pdb'
        rel_output = self.request.id + '/output.itp'
        rel_lack = self.request.id + '/lack.itp'
        # docker exec tpproject-tpp-1 runtppmktop.sh -i proc-simpl.pdb -o output.itp -l lack.itp -m -f OPLS-AA
        procres = subprocess.run(
            ['docker', 'exec',
             "--user", f"{os.getuid()}:{os.getgid()}",
             container_name, 'runtppmktop.sh',
             '-i', rel_input, '-o', rel_output, '-l', rel_lack,
             '-m',
             '--separate',
             '-f', 'OPLS-AA'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Capture stderr too
            text=True,                 # Decode to string
            check=True,                # Raise CalledProcessError on nonzero exit
            timeout=60
        )
        # save console output to the log
        with open(os.path.join(twd, 'console_output.log'), 'w') as fd:
            fd.write(procres.stdout)
        # move program log to project folder
        os.rename(
            os.path.join(container_vol, 'tppmktop.log'),
            os.path.join(twd, 'tppmktop.log')
        )
        logger.info("TPPMKTOP finished")
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Error running command: {e.cmd}\n"
            f"Exit code: {e.returncode}\n"
            f"Output: {e.output}"
        )
        res_pair = (1, twd)
    except SoftTimeLimitExceeded:
        logger.warning(f"Task {self.request.id} hit soft time limit. Cleaning up.")
        res_pair = (1, twd)
    else:
        logger.info("Normal execution!")
        res_pair = (0, twd)
    finally:
        logger.info(f"Calc-folder {twd} is scheduled to be cleaned in 5 min..")
        remove_tppmktop_folder.apply_async(countdown=300, args=[twd])
        return res_pair


@app.task(bind=True)
def remove_tppmktop_folder(self, folder_path):
    """
    Remove the TPPMKTOP folder after a delay.
    This function is intended to be run after a TPPMKTOP task completes.
    
    :param folder_path: Path to the folder to be removed
    """
    logger = self.app.log.get_default_logger()
    try:
        shutil.rmtree(folder_path)
        logger.info(f"Removed folder: {folder_path}")
    except Exception as e:
        logger.error(f"Error removing folder {folder_path}: {e}")

# Moking functions for testing purposes


@app.task(bind=True)
def moking_task_sleep(self, timeout):
    """
    Do nothing. Just sleep timeout seconds
    """
    time.sleep(timeout)
    return (timeout+1)

