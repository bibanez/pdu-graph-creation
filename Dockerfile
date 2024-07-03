FROM docker.io/openroad/ubuntu22.04-dev:latest

# Install system dependencies
RUN apt-get update && apt-get install -y wget build-essential libboost-all-dev

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
RUN bash miniconda.sh -b -p /opt/conda
ENV PATH="/opt/conda/bin:${PATH}"

# Create conda environment and install dependencies
RUN conda create -n gt -c conda-forge -y graph-tool tqdm
RUN echo "source activate gt" > ~/.bashrc
ENV PATH /opt/conda/envs/gt/bin:$PATH

# Install OpenDb
RUN git clone https://github.com/jonpry/OpenDb.git
RUN cd OpenDb && pip install . -v
RUN cd .. && rm -r OpenDb

WORKDIR /app

# Set the entrypoint to python3
ENTRYPOINT ["python3"]
