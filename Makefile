.PHONY: test upload clean bootstrap

DOCKER_MACHINE_NAME=small
DOCKER_ENGINE_VERSION=v1.8.1

clean:
	rm -rf *.egg-info
	rm -f **/*.pyc
	rm -f **/**/*.pyc
	rm -rf test/--pycache__
	rm -rf .cache
	rm -rf target
	docker-compose stop
	docker-compose rm -f

build: clean
	docker-compose build

test-dev:
	docker-compose up -d wildfly
	docker-compose run --rm wildfly-py-debug

test: build
	docker-compose up -d wildfly
	sleep 10
	docker-compose run --rm wildfly-py
	docker-compose stop
	docker-compose rm -f

ci: build
	docker-compose up -d wildfly
	sleep 10
	docker-compose run wildfly-py py.test --cov-report term --cov=wildfly-py --junitxml=target/TEST-reports.xml
	docker-compose stop
	docker-compose rm -f

package: test
	python setup.py sdist --dist-dir=target

upload-local: package
	cp ./target/wildfly-py-0.0.1.tar.gz ../docker-deployer/wildfly-py-0.0.1.tar.gz

upload: test
	python setup.py sdist upload
	make clean

register:
	python setup.py register

machine-create:

# TODO need to make sure dm is in Running status or Create/Start
#if docker-machine status $DOCKER_MACHINE_NAME; then
#    DOCKER_MACHINE_PRECREATED=true
#else
#    DOCKER_MACHINE_PRECREATED=false
#    create_machine $DOCKER_MACHINE_NAME
#fi

#if [ $DOCKER_MACHINE_PRECREATED = false ]; then
#    remove_machine $DOCKER_MACHINE_NAME
#fi

	docker-machine create \
                   --engine-insecure-registry docker.cenx.localnet:5000 \
                   -d virtualbox \
                   --virtualbox-boot2docker-url https://github.com/boot2docker/boot2docker/releases/download/${DOCKER_ENGINE_VERSION}/boot2docker.iso \
                   --virtualbox-disk-size "10000" \
                   ${DOCKER_MACHINE_NAME}

    # for DNS resolution when connect via VPN
    #docker-machine stop $DOCKER_MACHINE_NAME
    #VBoxManage modifyvm $DOCKER_MACHINE_NAME --natdnshostresolver1 on
    #docker-machine start $DOCKER_MACHINE_NAME
    #eval "$(docker-machine env $DOCKER_MACHINE_NAME)"

machine-rm:

	docker-machine rm -f ${DOCKER_MACHINE_NAME}

