while != nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

python manage.py migrate

python manage.py collectstatic --noinput

uwsgi --strict --ini uwsgi/uwsgi.ini