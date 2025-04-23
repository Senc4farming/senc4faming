WALGREEN
=============================================
WALGREEN: A platform for enhanced soil organic carbon (SOC) inference.  
Utilizes machine learning and cloud-based technologies to provide researchers with 
tools to access Soil Organic Carbon data(SOC).ç

Soil organic carbon (SOC) is a key indicator of soil health, fertility, and car-
bon sequestration, making it essential for sustainable land management and
climate change mitigation. However, large-scale SOC monitoring remains
challenging due to spatial variability, temporal dynamics, and multiple in-
fluencing factors. 

We present WALGREEN, a platform that enhances SOC inference by overcoming
limitations of current applications. Leveraging machine learning and diverse 
soil samples, WALGREEN generates predictive models using historical public 
and private data. Built on cloud-based tech nologies, it offers a user-friendly
interface for researchers, policymakers, and land managers to access carbon data, 
analyze trends, and support evidence-based decision-making.
Implemented in Python, Java, and JavaScript, WALGREEN integrates Google Earth Engine
and Sentinel Copernicus via scripting, OpenLayers, and Thymeleaf in a Model-View-Controller
framework.

Keywords: Soil organic carbon, machine learning, datasets, Sentinel
integration, Google Earth Engine integration, TIFF and GeoTIFF, Spring
Boot Framework, JPA, Python API with Flask, OpenLayers, JavaScript.

Preprint submitted to Environmental modelling & software April 23, 2025

![Platform main view1.png](webapp%2Fsrc%2Fmain%2Fresources%2Fstatic%2Fimg%2FPlatform%20main%20view1.png)

Architecture
================================================
![architecture.png](webapp%2Fsrc%2Fmain%2Fresources%2Fstatic%2Fimg%2Farchitecture.png)

WebApp frontend-backend
================================================
Code is located in folder webapp and deployment variables can be found in the .env file.
### Run the System
We can easily run the whole with only a single command:
```bash
docker compose -f .\docker-compose-desarrollo.yml up
docker compose -f .\docker-compose_prod.yml up

```

Docker will pull the MySQL and Spring Boot images (if our machine does not have it before).

The services can be run on the background with command:
```bash
docker compose -f .\docker-compose-desarrollo.yml up -d
docker compose -f .\docker-compose_prod.yml up -d
```

### Stop the System
Stopping all the running containers is also simple with a single command:
```bash
docker compose down
```

If you need to stop and remove all containers, networks, and all images used by any service in <em>docker-compose.yml</em> file, use the command:
```bash
docker compose down --rmi all
```

Python REST API Server : pos-restapi_sen4farming 
================================================
Code is located in api.This is a lightweight python3 REST API server that offers
essential web service features in a simple package.

**Table of contents**

* [Features](#features)
* [Building blocks](#building-blocks)
* [Run locally with Docker](#run-locally-with-docker)
* [Develop locally with Docker](#develop-locally-with-docker)
* [API methods](#api-methods)
* [Session data](#session-data)
* [Redis storage](#redis-storage)
* [Background workers & cron](#background-workers--cron)
* [License](#license)


Features
--------

A quick list of the features of this Python API server:

* Simple and flexible server with minimum dependencies
* Process-based request workers, not thread-based nor async
* Secure server-side sessions with Redis storage
* Robust worker management: restarts, timecapping, max life
* Background tasks
* Built-in cron
* Server reload on code change
* Docker image


Building blocks
---------------

The core building blocks of this server are mature open-source components that
I have years of experience of.

* [Python](http://python.org) is a high-level and versatile scripting language
  that provides powerful features with an exceptionally clear syntax.

* [Flask](http://flask.pocoo.org/) is the Python web framework. 

* [uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/) is the master daemon
  that runs and supervises the Python worker processes. 

* [PostgreSQL](http://postgresql.org) is the main database, 

* [Redis](https://redis.io/) is a persistent in-memory database that is used
  as a storage for server-side session data and as a lightweight caching and
  queueing system. Fast and solid.


Run locally with Docker
-----------------------
The server fully supports Docker - the Docker image is created with 
this [Dockerfile](Dockerfile).

The base image is an [official python image](https://hub.docker.com/_/python)
variant **hakonamdal/python-gdal:python3.9-gdal3.1.2**, adapted for geographical software.

If you already have Docker installed, the quick steps to run restpie-dev with
Postgres and Redis for first time are:

    # download latest postgresql version 12.x
    sudo docker run -d --name pos-restapisen4farming -p 5435:5435 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12

    # create + start the redis instance
    docker run -d --name redis -p 6379:6379 redis:5

    # Run and build api
    docker stop restpie-dev
    ./build.sh
    docker run --add-host=host.docker.internal:host-gateway -it --rm --name restpie-dev -p 8100:80  -v `pwd`/:/app/ -v /mnt/hgfs/solovmwarewalgreen/solovmwarewalgreen/projecto/SEN4CFARMING/api/files/:/app/files/   restpie-dev-image

The rest of the times we just need to run 3 commands to prepare API:
    sudo docker start redis
    sudo docker start pos-restapi_sen4farming
    sudo docker start restpie-dev
To stop API:
    docker stop redis
    docker stop pos-restpie
    docker stop restpie-dev


Develop locally with Docker
---------------------------

Docker is great for packaging software to be run in the cloud, but it is also
beneficial while developing the software. With Docker you can isolate and play
easily with different dev environments and services without installing
anything on the local machine and without facing ugly local version conflicts.
Running the same docker image locally also ensures the environment is
identical to the release environment, which makes a lot of sense.

    ./run.sh

The above command runs the dev instance in the foreground so you are able to
see the logging output in the console and detect errors immediately. You can
stop the server with CTRL+C.  When the instance ends, its data is deleted (the
--rm option) - this is good as we don't want to create a long list of dangling
temporary instances.


API methods
-----------

The available API methods are implemented in api_x.py modules:

* `api_ai_proc.py` contains the core api points for AI software .
* `api_gee_proc.py` contains the core api points for Google Earth Engine integration.
* `api_senfarming.py` contains the core api points for interaction with backend.
* `api_sentinelproc.py` contains the core api points for Copernicus integration.
  

Session data
------------

Server-side session data is stored in Redis. Data written into a session is
not visible at the client side.

Flask provides a thread-global session object that acts like a dictionary. You
set keys to values in the session. A value can be any object that can be
[pickled](https://docs.python.org/3/library/pickle.html). Modifications to the
session data are automatically saved to Redis by Flask at the end of the
request.


Background workers & cron
-------------------------

uwsgi provides a simple mechanism to run long running tasks in background
worker processes.


Deploy to Linux server running Docker
-------------------------------------

To be written. Docker compose, rsync+reload script etc.


License
-------
MIT License

