FROM python:3.15.2-slim-trixie
WORKDIR /app
RUN useradd --uid 10001 --create-home --shell /bin/bash app
COPY requirements.txt .
USER 10001
RUN pip install --user -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
