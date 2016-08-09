#!/bin/bash

jar cfm project-1.0.jar Manifest.txt HelloWorld.class

until $(curl -v -u admin:admin123 --upload-file project-1.0.jar http://nexus:8081/service/local/repositories/releases/content/com/project/1.0/project-1.0.jar); do 
    printf '.'
    sleep 5
done


