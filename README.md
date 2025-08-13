# TPP-webinterface

![Static Badge](https://img.shields.io/badge/Powered_by-Celery-blue?logo=celery)
![Static Badge](https://img.shields.io/badge/Powered_by-FastApi-009485?logo=fastapi)
![Static Badge](https://img.shields.io/badge/Powered_by-vue_2.7.x-blue?logo=vue.js)


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

# Production notes

For production, we do everything the same but proxy API and serve with NGINX.

1. Set up NGINX proxy for serve and proxy for API
```
server {
    listen 80;
    server_name mydomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name mydomain.com;

    ssl_certificate /etc/letsencrypt/live/mydomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mydomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

```
2. Set up `.env.production` in `./frontend` to
```
VUE_APP_API_URL=https://mydomain.com/api
```
3. Build frontend and run serve on localhost:8080
