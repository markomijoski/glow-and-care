#!/bin/sh
set -e

# Entrypoint: run migrations and collectstatic, then exec the CMD
# This expects environment variables (DATABASE_URL, DJANGO_SETTINGS_MODULE) to be provided at runtime.

echo "[entrypoint] running migrations (if any)..."
MAX_RETRIES=30
COUNT=0
until python manage.py migrate --noinput; do
	COUNT=$((COUNT+1))
	if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
		echo "[entrypoint] migrate failed after $COUNT attempts" >&2
		exit 1
	fi
	echo "[entrypoint] migrate failed, retrying in 10s..."
	sleep 10
done

echo "[entrypoint] collecting static files..."
python manage.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE:-CreamShop.settings.prod}

echo "[entrypoint] starting process: $@"
exec "$@"