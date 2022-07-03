if [ ! -d "${HOME}/.local" ]; then
    echo "Creating local python modules folder to map at ${HOME}/.local";
    mkdir -p "${HOME}/.local";
fi
