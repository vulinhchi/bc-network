FROM python:3.6

ENV PYTHONUNBUFFERED=1
RUN pip install --upgrade pip

RUN pip install flask requests pycrypto eth-account

ADD . /bc_network/my_blockchain

ENTRYPOINT cd /bc_network/my_blockchain && python main.py
