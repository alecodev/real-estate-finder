FROM python:3.11.3-alpine3.18

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

COPY ./src ./src

CMD [ "uvicorn", "--port", "5000", "--host", "0.0.0.0", "src.main:app" ]