 构建镜像：docker build -t novelserver .
 
  制作容器并运行：  
  docker run -it -v /home/docker_project/novelserver_docker/novelserver/book:/novelserver/book -v /home/docker_project/novelserver_docker/novelserver/configfiles:/novelserver/configfiles --name=novelserver novelserver
