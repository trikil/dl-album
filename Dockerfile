FROM continuumio/miniconda3

ARG USER_ID
ARG GROUP_ID

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y ffmpeg && rm -rf /var/lib/apt/lists/*

RUN addgroup --gid $GROUP_ID user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user
USER user

COPY environment.yaml .
RUN conda env create -f environment.yaml
SHELL ["conda", "run", "-n", "dl-album", "/bin/bash", "-c"]
RUN echo "conda activate dl-album" >> ~/.bashrc

ENV PYTHONUNBUFFERED=1

COPY . .

CMD ["conda", "run", "--no-capture-output", "-n", "dl-album", "python", "-u", "dl.py"]