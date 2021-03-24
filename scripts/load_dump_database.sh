echo '======= STOPPING ALL CONTAINERS AND DELETING VOLUMES'
docker-compose down --volumes

echo '======= STARTING DATABASE CONTAINER'
docker-compose up -d master-db

echo '======= DOWNLOADING DUMP FILE'
wget -O dump_db.gz https://gitlab.com/sige-gces-2020.2/sige-dump-devel/-/raw/master/dump_23-03-2021_22_54_06.gz?inline=false

echo '======= DECOMPRESSING  DUMP FILE'
gzip --decompress dump_db.gz

echo '======= LOADING  DUMP FILE'
cat dump_db | docker exec -i master-db psql -U postgres

echo '======= DELETING THE DOWNLOADED FILE'
rm dump_db
echo '======= DUMP SUCCESSFULLY LOADED'


echo '======= STARTING ALL CONTAINERS'
docker-compose up --detach

echo '======= DUMP SUCCESSFULLY LOADED'