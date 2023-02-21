# Junior Python FastAPI developer test task

## Start app
You need to have docker and docker-compose v1-v2 on your machine.

#### <span style="color:cyan">Create .env file </span>
<code> $ touch .env </code>  

#### <span style="color:cyan">Set shown below env vars in .env file</span>
""""  
DATABASE_URL=postgresql+asyncpg://postgres:postgres@webtronics-db/webtronics_db  
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=postgres  
POSTGRES_DB=webtronics_db  
SECRET_KEY=**SET RANDOM VALUE**   
HASH_ALGORITHM=**SET ALGORITHM VALUE**  
ACCESS_TOKEN_LIFETIME=**SET INT VALUE**  
REFRESH_TOKEN_LIFETIME=**SET INT VALUE**  
"""
#### <span style="color:cyan">Start app containers with docker-compose.yml file</span>
<code> $ docker compose up --build </code>

#### <span style="color:cyan">Go to http:0.0.0.0:8000/docs on your favorite browser! </span>


## To execute tests you need to create virtual environment, install dependencies and run tests
<code> poetry install </code>  
<code> pytest . </code>
