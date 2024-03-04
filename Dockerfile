FROM python:3.12

WORKDIR /app

COPY install.sh install.sh
RUN bash install.sh

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "/app/bot.py"] 
