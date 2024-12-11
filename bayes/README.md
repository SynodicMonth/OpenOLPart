## requirements

- docker

## Prepare environment

build docker image

```bash
cd environment/
docker build -t worloads .
```

run docker container and record the container id

```bash
cd ..
docker run -t -d --name=img-dnn -v $(pwd)/share:/tmp/share worloads # b7c786
docker run -t -d --name=masstree -v $(pwd)/share:/tmp/share worloads # e93de1
```

copy config script to container

```bash
docker cp config/run_gdw_img-dnn.sh img-dnn:/home/tailbench-v0.9/img-dnn
docker cp config/run_gdw_masstree.sh masstree:/home/tailbench-v0.9/masstree
```

set chmod

```bash
docker exec -it img-dnn chmod +x /home/tailbench-v0.9/img-dnn/run_gdw_img-dnn.sh
docker exec -it masstree chmod +x /home/tailbench-v0.9/masstree/run_gdw_masstree.sh
```


