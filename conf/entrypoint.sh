#!/bin/bash
set -e


# Define help message
show_help() {
    echo """
    Commands
    manage     : Invoke django manage.py commands
    setupdb  : Create empty database for vilogged, will still need migrations run
    """
}

setup_local_db() {
    set +e
    cd /code
    set -e
    python manage.py migrate
}

setup_prod_db() {
    set +e
    cd /code
    python manage.py migrate
}

case "$1" in
    manage )
        cd /code/
        python manage.py runserver
    ;;
    setuplocaldb )
        setup_local_db
    ;;
    setupproddb )
        setup_prod_db
    ;;
    test_coverage)
      python manage.py test --verbosity=2 --noinput
    ;;
    start )
        cd /code
        python manage.py collectstatic --noinput
        /usr/local/bin/supervisord -c /etc/supervisor/supervisord.conf
        nginx -g "daemon off;"
        python manage.py migrate
    ;;
    bash )
        bash
    ;;
    *)
        show_help
    ;;
esac