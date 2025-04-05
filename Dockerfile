FROM python:3-alpine

WORKDIR /app

RUN pip3 install python-tado

COPY ./tado_aa.py .
ENV GEOFENCING=geofencing
CMD ["python", "-u", "tado_aa.py"]