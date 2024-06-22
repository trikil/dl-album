FROM continuumio/miniconda3

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY environment.yaml .
RUN conda env create -f environment.yaml
SHELL ["conda", "run", "-n", "dl-album", "/bin/bash", "-c"]
RUN echo "conda activate dl-album" >> ~/.bashrc

ENV PYTHONUNBUFFERED=1

COPY . .

CMD ["conda", "run", "--no-capture-output", "-n", "dl-album", "python", "-u", "dl.py"]