# Downloadable environment

## About

This image enables new users to get started with ML-Git in a lightweight Linux-based image without worrying about configurations. The image also include a git repository with a predefined dataset and a minio instance populated with the dataset's data.

##### **How to use:**
1. Ensure that you have Docker installed.

2. Inside root of ML-Git directory build the image locally with the following command:
   
   `make docker.build`
   
   or
   
   `docker build -t mlgit_docker_env -f docker/Dockerfile .`

3. Run the Docker container to launch the built image:

   `make docker.run`
   
   or
   
   `docker run -it -p 8888:8888 --name mlgit_env mlgit_docker_env`

    Port 8888 will be used to start the jupyter notebook web service.
    
##### **Using the ML-Git with environment (inside docker container):**

The container has an ML-Git project initialized inside the directory workspace, the content of the versioned tag is an image from [mnist database](http://yann.lecun.com/exdb/mnist/). 

You can execute the command checkout directly to tag: 

```
ml-git datasets checkout handwritten__digits__mnist__1
```

##### **Summary of files in image:**

**local_server.git**  *(local git repository, used to store metadafiles).*<br/>
**data** *(directory used by the bucket to store project data).*<br/>
**init.sh** *(script that run basic command to use ml-git).*<br/>
**minio** *(minio executable).*<br/>
**local_ml_git_config_server.git** *(local git repositoy with configuration files, used by ml-git clone).*<br/>
**ml-git** *(source code of ml-git).*<br/>
**workspace** *(initialized ml-git project).*<br/>