WORKDIR={% if args.workdir %}{{ args.workdir }}{% elif workdir %}{{ workdir }}{% else %}$HOME{% endif %}
