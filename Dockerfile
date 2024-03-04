FROM python:3.12


WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN which python
RUN which python3
CMD ["python3", "/app/bot.py"] 
