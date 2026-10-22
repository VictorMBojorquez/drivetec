FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN useradd --system --create-home --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser . .
RUN python manage.py collectstatic --noinput && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=4)"
CMD sh -c "python manage.py migrate --noinput && gunicorn drivetec.wsgi -b 0.0.0.0:8000 -w 3"
