FROM mariadb:latest
LABEL authors="damiencortina"

ENTRYPOINT ["top", "-b"]