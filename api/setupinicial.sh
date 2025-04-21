sudo vmhgfs-fuse .host:/ /mnt/hgfs/solovmwarewalgreen -o allow_other -o uid=1000 -o nonempty
cd /mnt/hgfs/solovmwarewalgreen/solovmwarewalgreen/projecto/SEN4CFARMING/api/
sudo docker start redis
sudo docker start pos-restapi_sen4farming
sudo ./run.sh
