FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-kubernetes docker.io ansible && \
    rm -rf /var/lib/apt/lists/*