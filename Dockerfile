FROM python:3.12.3-alpine

EXPOSE 35101/tcp

ARG DATA_DIR
ENV DATA_DIR="/etc/lm-calendar"

ARG LIB_DIR
ENV LIB_DIR="/usr/lib/share/lm-calendar"

VOLUME [ "${DATA_DIR}" ]

COPY . ${LIB_DIR}
RUN chmod -R 755 ${LIB_DIR}
RUN chown -R root:root ${LIB_DIR}

RUN mkdir -p ${DATA_DIR}
RUN chmod -R 755 ${DATA_DIR}
RUN chown -R root:root ${DATA_DIR}

WORKDIR ${LIB_DIR}

RUN pip install --no-cache-dir .


CMD ["while", "[ 1 ];", "sleep 1;", "done"]