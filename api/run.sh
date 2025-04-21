#!/bin/sh
# run in dev mode
docker stop restpie-dev
./build.sh
docker run --add-host=host.docker.internal:host-gateway -it --rm --name restpie-dev -p 8100:80  -v `pwd`/:/app/ -v /mnt/hgfs/solovmwarewalgreen/solovmwarewalgreen/projecto/SEN4CFARMING/api/files/:/app/files/   restpie-dev-image  
