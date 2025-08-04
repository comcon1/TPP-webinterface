# TPP-webinterface

Web-interface for [TPPMKTOP](https://github.com/comcon1/TopologyPreProcessor). It uses docker-compose project [TPP-docker](https://github.com/comcon1/TPP-docker) which establishes the environment for `tppmktop` and bridges it to vue-application.

## Application structure
                                                         
```                                                                     
          ┌───────────────────────────────────────────────────┐      
          │ ┌───────────┐    ┌───────────────┐    ┌──────────┐│      
          │ │ Adminer   │    │  MariaDB      │    │ TPPMKTOP ││      
          │ │(DB editor)│◄──►│ tppforcefield │◄──►│ TPPRENUM ││      
          │ └───────────┘    └───────────────┘    └──────────┘│      
          │       Docker-network(comcon1/TPP-docker)    ▲     │      
          └─────────────────────────────────────────────┼─────┘      
                                                        │            
                                                        │            
                                                        ▼            
  ┌─────────────────┐     ┌────────────────┐    ┌────────────────┐   
  │      VUE        │     │    FastAPI     │    │    Celery      │   
  │   application   │◄──► │   interface    │◄──►│  task manager  │   
  │   (./frontend)  │     │  (./backend)   │    │  (./backend)   │   
  └─────────────────┘     └────────────────┘    └────────────────┘   
                                                        ▲            
                                                        │            
                                                        ▼            
                                                ┌────────────────┐   
                                                │     REDIS      │   
                                                │   (message     │   
                                                │      broker)   │   
                                                └────────────────┘   
```

## Setting up development environment

To set up development environment, one need to install docker and then synchornize [TPP-docker repository](https://github.com/comcon1/TPP-docker). Let's assume we are working in `~/repo`:

```bash
cd ~/repo/
git clone https://github.com/comcon1/TPP-docker
cd TPP-docker/compose
./deploy.sh
```

Check that everything is finally OK:

```
$ ~/repo/TPP-docker$ docker ps --format "table {{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}"
IMAGE                   STATUS                PORTS                                         NAMES
comcon1/tppcon:latest   Up 7 days                                                           tpproject-tpp-1
wodby/adminer           Up 7 days             0.0.0.0:9000->9000/tcp, [::]:9000->9000/tcp   tpproject-adminer-1
wodby/mariadb           Up 7 days (healthy)   3306/tcp                                      tpproject-mariadb-1
```

Now you have a folder `~/repo/TPP-docker/compose/volume/work` for communication with the main container `tpproject-tpp-1`.

Then clone and install everything for this repo (will assume for simplicity using `uv`):
```bash
cd ~/repo
git clone https://github.com/comcon1/TPP-webinterface
cd TPP-webinterface/backend
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Finally, install everything required for the application:
```bash
systemctl start redis-server
cd backend
screen -dmS backend uvicorn tppapi:app --reload
screen -dmS taskmanager celery -A celery_tasks worker --loglevel=info
cd ../frontend
screen -dmS npm npm run serve
```