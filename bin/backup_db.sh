docker-compose run --rm app python3 manage.py dumpdata --exclude auth.permission --exclude contenttypes > "db_backup_$(date +"%d-%m-%y").json"