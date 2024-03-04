local_run:
	python bot.py

build:
	docker build -t passbot-bot -f Dockerfile .

run:
	docker run -d passbot-bot:latest
