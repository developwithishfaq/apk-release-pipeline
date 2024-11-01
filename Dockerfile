FROM ubuntu:latest

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /data

ENV JKS_NAME=ishfaq.jks
ENV SCRIPT=build.sh
ENV REPO_LINK="https://github.com/developwithishfaq/mon"

COPY ./data/keys/$JKS_NAME ./jks/

COPY ./data/scripts/$SCRIPT ./scripts/

# Make the script executable
RUN chmod +x ./scripts/$SCRIPT

ENTRYPOINT ["/bin/sh", "-c", "./scripts/$SCRIPT"]

CMD [ "/bin/bash" ]