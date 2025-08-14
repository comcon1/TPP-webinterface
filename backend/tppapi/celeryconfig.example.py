# Here we recommend to use simple redis installation
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
# this is TPP container name. It should be corrected
CONTAINER_NAME = 'tpproject-tpp-1'
# this is your absolute path to mounted work-volume
CONTAINER_VOL = '/home/comcon1/repo/TPP-docker/compose/volume/work'
# -------------------------------------------------------------------------------------------------------------
# These commands are related to log 
worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
worker_task_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(task_name)s[%(task_id)s]: %(message)s"
worker_redirect_stdouts_level = 'INFO'
