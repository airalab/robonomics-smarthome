FROM python:3.9
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY illumination.py illumination.py
COPY illumination_config.yaml illumination_config.yaml
RUN mkdir data
CMD ["python3", "illumination.py"]