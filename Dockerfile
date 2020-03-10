FROM continuumio/miniconda:latest

WORKDIR /home/my-fund

COPY environment.yml ./
COPY *.py ./
COPY Fund.xlsx ./
COPY boot.sh ./

RUN chmod +x boot.sh

RUN conda env create -f environment.yml

RUN echo "source activate my-fund" > ~/.bashrc
ENV PATH /opt/conda/envs/my-fund/bin:$PATH

ENTRYPOINT ["./boot.sh"]
