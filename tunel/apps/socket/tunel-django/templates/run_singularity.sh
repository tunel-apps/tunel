SIF="${SINGULARITY_CACHEDIR}/tunel-django.sif"
CONTAINER="{% if args.container %}{{ args.container }}{% else %}docker://ghcr.io/tunel-apps/tunel-django:{% if args.tag %}{{ args.tag }}{% else %}latest{% endif %}{% endif %}"

if command -v singularity &> /dev/null
then
    printf "singularity pull ${CONTAINER}\n"

    # Bind migrations directories
    migrations_main=${SOCKET_DIR}/db/main-migrations
    migrations_user=${SOCKET_DIR}/db/user-migrations

    mkdir -p ${DB_DIR} ${STATIC_DIR} ${migrations_main} ${migrations_user}

    # Only pull the container if we do not have it yet, or the user requests it
    if [[ ! -f "${SIF}" ]] || [[ "{{ args.pull }}" != "" ]]; then
        singularity pull --force ${SIF} ${CONTAINER}
    fi
    
    # The false at the end ensures we aren't using nginx, but rather uwsgi just with sockets
    printf "singularity exec --bind ${DB_DIR}:/code/db --env TUNEL_PASS=***** --env TUNEL_USER=***** --bind ${migrations_main}:/code/tuneldjango/apps/main/migrations --bind ${migrations_user}:/code/tuneldjango/apps/users/migrations --bind ${STATIC_DIR}:/code/static --bind ${WORKDIR}:/code/data ${SIF} /bin/bash /code/scripts/run_uwsgi.sh ${SOCKET} false\n"
    # The bind for WORKDIR to /var/www/data ensures the filesystem explorer works
    singularity exec --bind ${DB_DIR}:/code/db --env TUNEL_PASS=${TUNEL_PASS} --env TUNEL_USER=${TUNEL_USER} --bind ${migrations_main}:/code/tuneldjango/apps/main/migrations --bind ${migrations_user}:/code/tuneldjango/apps/users/migrations --bind ${STATIC_DIR}:/code/static --bind ${WORKDIR}:/code/data ${SIF} /bin/bash /code/scripts/run_uwsgi.sh ${SOCKET} false
else
    printf "Singularity is not available.\n"
fi
