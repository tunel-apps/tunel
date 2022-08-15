CONTAINER="{% if args.container %}{{ args.container }}{% else %}ghcr.io/tunel-apps/tunel-django:{% if args.tag %}{{ args.tag }}{% else %}latest{% endif %}{% endif %}"

if command -v {{ docker }} &> /dev/null
then
    if [[ "{{ args.pull }}" != "" ]]; then
        {{ docker }} pull ${CONTAINER}
    fi

    mkdir -p ${DB_DIR} ${STATIC_DIR} ${migrations_main} ${migrations_user}

    # Important: remove t here because we already are in terminal (will get error)
    printf "{{ docker }} run -d -i --rm --name {{ jobslug }} --entrypoint /bin/bash --env TUNEL_PASS=***** --env TUNEL_USER=***** -v ${STATIC_DIR}:/code/static -v ${WORKDIR}:/code/data ${CONTAINER} /code/scripts/run_uwsgi.sh ${SOCKET} false\n"
    # The bind for WORKDIR to /var/www/data ensures the filesystem explorer works
    {{ docker }} run -d -i --rm --name {{ jobslug }} --entrypoint /bin/bash --env TUNEL_PASS=${TUNEL_PASS} --env TUNEL_USER=${TUNEL_USER} -v ${STATIC_DIR}:/code/static -v $HOME:$HOME -v ${WORKDIR}:/code/data ${CONTAINER} /code/scripts/run_uwsgi.sh ${SOCKET} false\n
    printf "Container is ready...\n"
else
    printf "{{ docker }} is not available.\n"
fi
