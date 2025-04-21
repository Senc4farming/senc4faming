sudo vmhgfs-fuse .host:/ /mnt/hgfs/solovmwarewalgreen -o allow_other -o uid=1000 -o nonempty
cd /mnt/hgfs/solovmwarewalgreen/solovmwarewalgreen/projecto/api/
docker start redis
docker start pos-restapi_sen4farming
./run.sh 
