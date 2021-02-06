FROM python:3.8-slim
  
RUN apt-get -qq update && \
    apt-get -qq -y install ffmpeg gcc && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/*

COPY ./ /app/
WORKDIR /app
RUN pip3 install -r requirements.txt

RUN for file in ./plugins/*/requirements.txt; \
    do \
        cat $file >> plugins_requrements.txt;\
    done 
RUN ls
RUN pip3 install -r plugins_requrements.txt

ENTRYPOINT ["python3", "/app/main.py", "--config", "/app/config/config.ini"]
