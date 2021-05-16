FROM python:3.9

ADD code /code
RUN pip install -r /code/requirements.txt

WORKDIR /code
ENV PYTHONPATH '/code/'

CMD ["python" , "/code/collector.py"]