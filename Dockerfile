FROM python:3.9-alpine

RUN addgroup -S hubibtpresence && adduser -S hubibtpresence -G hubibtpresence

# The app relies on btmgmt (bluez-btmgmt package) that needs root privileges (sudo).
RUN apk add --no-cache sudo bluez-btmgmt
RUN echo '%hubibtpresence  ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER hubibtpresence

WORKDIR /app

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1
# Install location of upgraded pip
ENV PATH /home/hubibtpresence/.local/bin:$PATH

COPY requirements.txt     /app

RUN pip install --no-cache-dir --disable-pip-version-check --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

COPY *.py                 /app/
COPY template.config.yaml /app/

ENTRYPOINT python main.py
