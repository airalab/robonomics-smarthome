FROM python:3.6
COPY python_scripts/utils.py python_scripts/utils.py
COPY python_scripts/config.config python_scripts/config.config
COPY python_scripts/run_sds.py python_scripts/run_sds.py
RUN pip3 install pynacl packaging pycurl pyserial
RUN pip3 install substrate-interface==1.1.2
CMD ["python3", "python_scripts/run_sds.py"]