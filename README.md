Install required system packages:

    sudo apt-get install python3-pip

Create www directory where project sites and environment dir

    mkdir /var/www && mkdir /var/envs

Install virtualenv
    
    pip install virtualenv

Create virtualenv

    cd /var/envs && python -m venv ds-assignment && ./ds-assignment/bin/activate

Install requirements for a project.

    cd /var/www/ds_assignment && pip install -r requirements.txt


## RUN FastAPI app

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

## OR

## Install Docker and docker-compose. (Recommended)

### Run this:

    ```bash
    docker-compose -f docker-compose.yml build
    docker-compose -f docker-compose.yml up -d
    ```
