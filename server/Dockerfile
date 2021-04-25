FROM python:3
ARG CODE_MASTERPLAYER


WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN sed -i -r "s/masterplayer/$CODE_MASTERPLAYER/g" ./server.py



#CMD [ "python", "./server.py" ]
