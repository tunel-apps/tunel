SIF="${SINGULARITY_CACHEDIR}/neurodesk.sif"
CONTAINER="docker://{% if args.container %}{{ args.container }}{% else %}ghcr.io/neurodesk/caid/itksnap_3.8.0:{% if args.tag %}{{ args.tag }}{% else %}20210322{% endif %}{% endif %}"

if command -v singularity &> /dev/null
then
    printf "singularity pull ${CONTAINER}\n"

    # Only pull the container if we do not have it yet, or the user requests it
    if [[ ! -f "${SIF}" ]] || [[ "{{ args.pull }}" != "" ]]; then
        singularity pull --force ${SIF} ${CONTAINER}
    fi
    
    # The false at the end ensures we aren't using nginx, but rather uwsgi just with sockets
    printf "singularity run ${SIF}\n"
    # Likely we could allow some custom binds here
    singularity run ${SIF}

else
    printf "Singularity is not available.\n"
fi
