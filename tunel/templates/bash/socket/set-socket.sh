SOCKET="${SOCKET_DIR}/{{ jobslug }}.sock"
if [[ -f "${SOCKET}" ]]; then
    echo "Removing existing socket ${SOCKET}"
    rm ${SOCKET}
fi

# Remove other sockets
rm -rf ${SOCKET_DIR}/*.sock
