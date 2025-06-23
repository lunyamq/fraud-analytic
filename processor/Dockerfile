FROM bitnami/spark:3.5

USER root
RUN install_packages python3 python3-pip unzip
RUN pip3 install kafka-python pandas tqdm

WORKDIR /app
COPY . /app

RUN chmod +x download.sh

CMD ["tail", "-f", "/dev/null"]
