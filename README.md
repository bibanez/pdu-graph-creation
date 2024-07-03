# pdu-graph-creation
Generate graph structures from LEF/DEF designs using OpenDB. Currently only supports output to graph-tools `.gt` format.

## Instructions

### Build image

The easiest way to execute this program is using [Docker](https://docs.docker.com/get-docker/).
After installing it, we can build the docker image described in `Dockerfile` like this:

```bash
docker build -t graph-generator .
```

### Executing the program

> Note: The Python program needs to have access to the folders from where it will get LEF/DEF files and also where it will save the output. In the following command we only give it access to the current folder so we need to have design files saved here.

An example execution of the program is the following:

```bash
docker run --rm -it -v $(pwd):/app graph-generator generate_graph.py designs/tech.lef designs/design.def sample_out.gt
```

Be sure to change the .lef and .def files as well as the output path to suit your application
