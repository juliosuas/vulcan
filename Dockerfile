FROM python:3.12-slim

LABEL maintainer="Vulcan Team"
LABEL description="AI-Powered Autonomous Penetration Testing Agent"

RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    dnsutils \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir nuclei subfinder gobuster 2>/dev/null || true

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

ENTRYPOINT ["vulcan"]
CMD ["--help"]
