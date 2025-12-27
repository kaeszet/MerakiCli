FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY meraki_cli.py .

ENV MERAKI_DASHBOARD_API_KEY=""

ENTRYPOINT ["python", "meraki_cli.py"]