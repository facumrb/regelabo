FROM ubuntu:22.04

# Variables de versión
ARG CC3D_VERSION=4.6.0
ARG PYTHON_VERSION=3.10

# Dependencias del sistema y GUI
RUN apt-get update && apt-get install -y \
    wget curl bzip2 build-essential pkg-config \
    libglib2.0-dev libgtk-3-dev libglu1-mesa libxi6 libxrender1 \
    xvfb x11vnc fluxbox novnc websockify \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar CompuCell3D oficial
WORKDIR /opt
RUN curl -L "https://sourceforge.net/projects/cc3d/files/rc-${CC3D_VERSION}/linux/cc3d-installer-linux-${CC3D_VERSION}-x86-64bit.sh/download" -o cc3d-installer.sh \
    && chmod +x cc3d-installer.sh \
    && ./cc3d-installer.sh --mode unattended --prefix /opt/CC3D \
    && rm cc3d-installer.sh

ENV PATH="/opt/CC3D:${PATH}"

# Instalar Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh \
    && bash miniconda.sh -b -p /opt/conda \
    && rm miniconda.sh
ENV PATH="/opt/conda/bin:${PATH}"

# Crear entorno científico avanzado (Bibliotecas científicas + ML + Jupyter)
RUN conda create -n cc3d_env python=${PYTHON_VERSION} -y \
    && conda run -n cc3d_env conda install -c conda-forge -c pytorch \
    numpy scipy matplotlib pandas seaborn scikit-learn \
    jupyterlab pytorch torchvision cpuonly \
    sympy statsmodels scikit-image plotly bokeh \
    h5py openpyxl networkx \
    -y \
    && conda clean -afy

# Configuración de pantalla y puertos (noVNC y JupyterLab)
ENV DISPLAY=:1
EXPOSE 6080 8888

WORKDIR /home/cc3d

# Script de inicio para manejar la GUI, noVNC y JupyterLab (Arquitectura Dual)
RUN echo '#!/bin/bash\n\
Xvfb :1 -screen 0 1280x800x24 &\n\
sleep 2\n\
fluxbox &\n\
x11vnc -display :1 -nopw -forever -quiet &\n\
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080 &\n\
conda run --no-capture-output -n cc3d_env jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password="" &\n\
echo "Laboratorio Virtual listo:"\n\
echo "  - Interfaz GUI (noVNC): http://localhost:6080/vnc.html"\n\
echo "  - Interfaz Notebook (JupyterLab): http://localhost:8888"\n\
conda run --no-capture-output -n cc3d_env bash' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
