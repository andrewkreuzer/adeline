FROM python:latest as builder
RUN apt-get update && apt-get clean
COPY requirements.txt /build/
WORKDIR /build/
RUN pip install -U pip && pip install -r requirements.txt

FROM python:latest as app
COPY --from=builder /build/ /app/
COPY --from=builder /usr/local/lib/ /usr/local/lib/
WORKDIR /app/
COPY adeline/*.py /app/
RUN useradd -ms /bin/bash  adeline
USER adeline
ENTRYPOINT python main.py
