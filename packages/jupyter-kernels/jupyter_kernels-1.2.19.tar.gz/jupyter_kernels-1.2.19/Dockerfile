# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

FROM python:3.11

RUN mkdir /opt/jupyter-kernels

WORKDIR /opt/jupyter-kernels

RUN pip install kazoo

COPY jupyter_kernels /opt/jupyter_kernels
RUN pip install -e ./jupyter_kernels

# COPY frontplane/dist.html /opt/jupyter-kernels/index.html

WORKDIR /opt/jupyter-kernels/editor

EXPOSE 9300

CMD ["python", "-m", "jupyter_kernels"]
