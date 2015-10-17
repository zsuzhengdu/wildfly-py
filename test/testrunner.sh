#!/usr/bin/env bash

run() {

    #mode="daemon"
    mode="dev"
    if [ "$mode" = "daemon" ]; then
        docker run --rm -t \
               -v $CORTX_HOME:/opt/cenx  \
               -v $DOCKER_CERT_PATH:/root/.docker \
               -e DOCKER_HOST=$DOCKER_HOST -e DOCKER_MACHINE_NAME=$DOCKER_MACHINE_NAME \
               -e DOCKER_TLS_VERIFY=$DOCKER_TLS_VERIFY \
               --entrypoint=/tmp/wildfly-py/test/unittests.py docker.cenx.localnet:5000/wildfly-py --failfast $@
    else
        docker run --rm -it \
               -v `pwd`:/code  \
               -v $DOCKER_CERT_PATH:/root/.docker \
               -e DOCKER_HOST=$DOCKER_HOST -e DOCKER_MACHINE_NAME=$DOCKER_MACHINE_NAME \
               -e DOCKER_TLS_VERIFY=$DOCKER_TLS_VERIFY \
               --entrypoint=/bin/bash docker.cenx.localnet:5000/wildfly-py
    fi
        
}

create_machine() {

    DOCKER_ENGINE_VERSION="v1.8.1"
    DOCKER_MACHINE_NAME=$1
    docker-machine create \
                   --engine-insecure-registry docker.cenx.localnet:5000 \
                   -d virtualbox \
                   --virtualbox-boot2docker-url https://github.com/boot2docker/boot2docker/releases/download/${DOCKER_ENGINE_VERSION}/boot2docker.iso \
                   --virtualbox-disk-size "10000" \
                   $DOCKER_MACHINE_NAME

    # for DNS resolution when connect via VPN
    #docker-machine stop $DOCKER_MACHINE_NAME
    #VBoxManage modifyvm $DOCKER_MACHINE_NAME --natdnshostresolver1 on
    #docker-machine stop $DOCKER_MACHINE_NAME
    
}

remove_machine() {
   docker-machine rm -f $1
}


DOCKER_MACHINE_NAME="small"
# TODO need to make sure dm is in Running status or Create/Start
if docker-machine status $DOCKER_MACHINE_NAME; then
    DOCKER_MACHINE_PRECREATED=true
else
    DOCKER_MACHINE_PRECREATED=false
    create_machine $DOCKER_MACHINE_NAME
fi

eval "$(docker-machine env $DOCKER_MACHINE_NAME)"
docker build --rm -t docker.cenx.localnet:5000/wildfly-py .
run $@

if [ $DOCKER_MACHINE_PRECREATED = false ]; then
    remove_machine $DOCKER_MACHINE_NAME
fi

exit
