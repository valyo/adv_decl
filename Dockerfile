# set base image (host OS)
FROM python:3.8 AS builder

COPY requirements.txt .

# install dependencies to the local user directory (eg. /root/.local)
RUN pip install --user -r requirements.txt

# second unnamed stage
FROM python:3.8-slim
WORKDIR /code

# copy only the dependencies installation from the 1st stage image
COPY --from=builder /root/.local /root/.local
# copy the dependencies file to the working directory

# copy the content of the local src directory to the working directory
COPY src/ .

# command to run on container start
CMD [ "python", "./adv_decl.py" ]
# CMD [ "python", "./adv_decl.v01.py" ]


