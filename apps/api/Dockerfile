# Microsoft's official Playwright image, not a bare python:slim + hand-rolled
# apt-get list: it ships every system library Chromium (and WeasyPrint's
# Pango/cairo/gdk-pixbuf stack) needs, pre-tested for this exact Playwright
# version. Building on a floating "python:slim" tag repeatedly broke here as
# Debian renamed/dropped packages between releases (e.g. gdk-pixbuf,
# ttf-unifont) — pin the version to match the `playwright` pin in
# requirements.txt whenever that changes.
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
