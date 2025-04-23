WALGREEN
=============================================
Soil organic carbon (SOC) is a key indicator of soil health, fertility, and car-
bon sequestration, making it essential for sustainable land management and
climate change mitigation. However, large-scale SOC monitoring remains
challenging due to spatial variability, temporal dynamics, and multiple in-
fluencing factors. We present WALGREEN, a platform that enhances SOC
inference by overcoming limitations of current applications. Leveraging ma-
chine learning and diverse soil samples, WALGREEN generates predictive
models using historical public and private data. Built on cloud-based tech-
nologies, it offers a user-friendly interface for researchers, policymakers, and
land managers to access carbon data, analyze trends, and support evidence-
based decision-making. Implemented in Python, Java, and JavaScript, WAL-
GREEN integrates Google Earth Engine and Sentinel Copernicus via script-
ing, OpenLayers, and Thymeleaf in a Model-View-Controller framework.
This paper aims to advance soil science, promote sustainable agriculture,
and drive critical ecosystem responses to climate change.
Keywords: Soil organic carbon, machine learning, datasets, Sentinel
integration, Google Earth Engine integration, TIFF and GeoTIFF, Spring
Boot Framework, JPA, Python API with Flask, OpenLayers, JavaScript.

Preprint submitted to Environmental modelling & software April 23, 2025



WebApp backend-frontend
================================================

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


This is a lightweight python3 REST API server that offers
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
* [Tests](#tests)
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
* Tests for the API


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
variant **python:3.9-slim-buster**, a recent and small Debian.

If you already have Docker installed, the quick steps to run RESTPie3 with
SQLite and Redis are:

    # download latest redis version 5.x
    docker pull redis:5

    # create + start the redis instance
    docker run -d --name redis -p 6379:6379 redis:5

    # download and build RESTPie3
    git clone https://github.com/tomimick/restpie3
    cd restpie3
    ./build.sh

    # start RESTPie3
    ./run.sh

    # in another term, create initial database schema
    docker exec -it restpie-dev bash -l -c 'python /app/scripts/dbmigrate.py'


If all went OK, RESTPie3 + Redis are running and you should be able to list
the REST API at http://localhost:8100/api/list

The SQLite database is empty at this point so empty lists are returned from
the API.  You are also logged out so some of the API end-points can't be
accessed. To quickly test the API, you can invoke this example script which
uses curl to do a signup and insert a new movie in the database:

    ./test/quick.sh

For a serious setup you want to have full PostgreSQL. Do the setup like this:

    # download latest postgresql version 12.x
    docker pull postgres:12

    # create + start a postgres instance - use your own db + password!
    # the params here must match the ones in conf/server-config.json
    docker run -d --name pos-restpie -p 5432:5432 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=MY_PASSWORD postgres:12

    # activate the uuid extension
    docker exec -it pos-restpie psql -U tm -d tmdb -c 'create extension "uuid-ossp"'

    # and then in server-config.json
    # set PYSRV_DATABASE_HOST (see PYSRV_DATABASE_HOST_POSTGRESQL)

To start and stop these docker instances, invoke:

docker run -d --name pos-restpie -p 5432:5432 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1789  sudo docker run -d --name pos-restpie -p 5432:5432 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1790  sudo docker run -d --name pos-restpie -p 5433:5432 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1791  sudo docker run -d --name pos-restsen4farming -p 5433:5432 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1792  sudo docker run -d --name pos-restsen4farming -p 5433:5433 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1793  sudo docker run -d --name pos-apisen4farming -p 5433:5433 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1797  sudo docker run -d --name pos-apisen4farming -p 5434:5434 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1798  sudo docker run -d --name pos-restapisen4farming -p 5435:5435 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1800  sudo docker run -d --name pos-restapi-sen4farming -p 5435:5432 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1801  sudo docker run -d --name pos-restapi-sen4farming -p 5436:5432 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1802  sudo docker run -d --name pos-restapi_sen4farming -p 5436:5432 -e POSTGRES_DB=tmdb -e POSTGRES_USER=tm -e POSTGRES_PASSWORD=eneas postgres:12
 1803  sudo docker run --add-host=host.docker.internal:host-gateway -it --rm --name restpie-dev -p 8100:80 -v `pwd`/:/app/ restpie-dev-image 



    sudo docker start redis
    sudo docker start pos-restpie
    sudo docker start pos-restapi_sen4farming
    sudo docker start restpie-dev
    docker stop redis
    docker stop pos-restpie
    docker stop restpie-dev

If you don't want to use docker, you can install Redis, PostgreSQL, python3
and the required python libs on your local machine too. On OSX,
[Homebrew](https://brew.sh/) is a good installation tool. These steps are not
documented here, but it's not that hard.


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

Now the COOL thing in the dev mode here is that we are using Docker volumes to
map a local root folder containing all source files to `/app/` folder
inside the Docker instance. This makes it possible to use any local file
editor to edit the python sources and when a file is saved, the server inside
the Docker instance reloads itself automatically!

To see the executed SQL statements of the server in the console, you can set
the PYSRV_LOG_SQL env variable:

    docker run -it --rm --name restpie-dev -p 8100:80 -v `pwd`/:/app/ -e PYSRV_LOG_SQL=1 restpie-dev-image


If you want to run a shell inside the dev instance, invoke in another terminal
session, while dev instance is running:

    docker exec -it restpie-dev bash -l

    # or just
    ./shell.sh

    # see files in the instance file system
    ls
    ll

    # see running processes
    htop

    # run python files
    python scripts/something.py

You can modify the [login script](conf/loginscript.sh) to set paths and
aliases etc for this interactive shell.


API methods
-----------

The available API methods are implemented in api_x.py modules:

* `api_account.py` contains the core email/password login/signup/logout
  methods that you most likely need anyway.
* `api_dev.py` contains misc methods for testing and developing which you can
  discard after learning the mechanics.
* `api_movies.py` is just a sample module to demonstrate a basic CRUD REST
  API.  You definately want to discard this and transform into your actual
  data models - just read and learn it.


Session data
------------

Server-side session data is stored in Redis. Data written into a session is
not visible at the client side.

Flask provides a thread-global session object that acts like a dictionary. You
set keys to values in the session. A value can be any object that can be
[pickled](https://docs.python.org/3/library/pickle.html). Modifications to the
session data are automatically saved to Redis by Flask at the end of the
request.

This starter stores two core data in the session: `userid` and `role` of the
user. (Role-field is in session for performance reason: otherwise we would
need to query it from the database with EVERY request that specifies
login_required. Note that if the user role changes, you need to update it in
session too.)

A common operation in an API method is to access the calling user object,
myself.  There is a call `webutil.get_myself()` that loads myself from the
database, or None for a visitor.

Flask also provides a thread-global object called `g` where you can store
data, but this data is *only stored for the duration of the request.* This
data is not stored in Redis and is discarded when the request ends. `g` can be
used for caching common data during the request, but don't overuse it.

Redis is a persistent storage, unlike memcached, which means that if the
server gets rebooted, the user sessions will be restored and logged-in users
do not need to relogin.

By default, the session is remembered for 1 month. If there is no user
activity during 1 month, the session gets deleted. This time is controlled by
PERMANENT_SESSION_LIFETIME in [config.py](py/config.py).


Redis storage
-------------

You can also use Redis for other than session data. Redis can act as a
convenient schema-free storage for various kinds of data, perhaps for
temporary data, or for lists whose size can be limited, or act as a
distributed cache within a cluster of servers.

A typical case might be that a background worker puts the calculation results
into Redis where the data is picked from by an API method (if the result is
secondary in nature and does not belong to the master database).

The module [red.py](py/red.py) provides simple methods for using Redis:

```python
    # store a value into Redis (here value is a dict but can be anything)
    value = {"type":"cat", "name":"Sophia"}
    red.set_keyval("mykey", value)

    # get a value
    value = red.get_keyval("mykey")

    # store a value that will expire/disappear after 70 minutes:
    red.set_keyval("cron_calculation_cache", value, 70*60)
```

To append data into a list:

```python
    # append item into a list
    item = {"action":"resize", "url":"https://example.org/a.jpg"}
    red.list_append("mylist", item)

    # take first item from a list
    item = red.list_pop("mylist")

    # append item into a FIFO list with a max size of 100
    # (discards the oldest items first)
    red.list_append("mylist", data_item, 100)
```

red.py can be extended to cover more functionality that
[Redis provides](https://redis.io/commands).


Background workers & cron
-------------------------

uwsgi provides a simple mechanism to run long running tasks in background
worker processes.

In any Python module (like in [bgtasks.py](py/bgtasks.py)) you have code
to be run in a background worker:

```python
    @spool(pass_arguments=True)
    def send_email(*args, **kwargs):
        """A background worker that is executed by spooling arguments to it."""
        #...code here...
```

You start the above method in a background worker process like this:

```python
    bgtasks.send_email.spool(email="tomi@tomicloud.com",
            subject="Hello world!", template="welcome.html")
```

The number of background worker processes is controlled by `spooler-processes`
configuration in [uwsgi.ini](conf/uwsgi.ini). The spooled data is written and
read into a temp file on disk, not in Redis.

Crons are useful for running background tasks in specified times, like in
every hour or every night. uwsgi has an easy built-in support for crons. To
have a nightly task you simple code:

```python
    @cron(0,2,-1,-1,-1)
    #(minute, hour, day, month, weekday) - in server local time
    def daily(num):
        """Runs every night at 2:00AM."""
        #...code here...
```


Tests
-----

The test folder contains two test scripts for testing the server API and the
Redis module. Keeping tests up-todate and running them frequently or
automatically during the process is a safety net that protects you from
mistakes and bugs.  With dynamic languages such as Python or Javascript or
Ruby, tests are even more important than with compiled languages.

For locally run tests I expose a method `/apitest/dbtruncate` in
[api_dev.py](py/api_dev.py) that truncates the data in the database tables
before running the API tests. If you like to write tests in a different way,
just remove it.

Run tests inside the DEV instance:

    docker exec -it restpie-dev bash -l -c 'python /app/test/test_api.py'
    docker exec -it restpie-dev bash -l -c 'python /app/test/test_redis.py'


Deploy to Linux server running Docker
-------------------------------------

To be written. Docker compose, rsync+reload script etc.


License
-------
MIT License

