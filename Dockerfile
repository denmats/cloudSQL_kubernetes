FROM ubuntu:16.04

COPY ./csv/*.csv ./opt/

RUN apt-get update \
     && apt-get install -y mysql-client \
         telnet \
         net-tools \
         curl \
         iputils-ping \
         netcat \
         redis-tools \
         default-jre
ENTRYPOINT  ["/bin/bash", "-c", "tail -f /dev/null"]

CMD ["while true; do sleep 30; done;"]

