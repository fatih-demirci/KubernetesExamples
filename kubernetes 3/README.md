# 3

- [3](#3)
  - [Docker](#docker)
    - [Ayağa kaldırılacak olan uygulama app.py](#ayağa-kaldırılacak-olan-uygulama-apppy)
    - [Uygulamanın Dockerfile'ı requirements.txt içine uygulamanın bağımlılığı olan Flask yazılarak hazırlanır](#uygulamanın-dockerfileı-requirementstxt-içine-uygulamanın-bağımlılığı-olan-flask-yazılarak-hazırlanır)
    - [Docker-compose.yml](#docker-composeyml)
  - [Deployment](#deployment)
  - [LoadBalancer Service](#loadbalancer-service)
  - [LoadBalancer servis üzerinden erişim](#loadbalancer-servis-üzerinden-erişim)         
  - [Ölçeklendirme](#ölçeklendirme)
#
## Docker
### Ayağa kaldırılacak olan uygulama app.py

```python
from flask import Flask
import socket

app = Flask(__name__)


@app.route('/')
def hello_world():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)

    return f'Hostname: {host_name} Hostip: {host_ip} \n'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Uygulamanın Dockerfile'ı requirements.txt içine uygulamanın bağımlılığı olan Flask yazılarak hazırlanır

```Dockerfile
FROM python:3.7

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Docker-compose.yml

```yml
version: '3'
services:
  s_flask_api:
    image: flaskapi
    container_name: c_flask_api
    build: .
    ports:
      - "5000:5000"
```
`docker-compose build` ile derlenerek image oluşturulur

## Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-api-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flask-api
  template:
    metadata:
      labels:
        app: flask-api
    spec:
      containers:
        - name: flask-api
          imagePullPolicy: IfNotPresent
          image: flaskapi:latest
          resources:
            requests:
              memory: "32Mi"
              cpu: "125m"
            limits:
              memory: "64Mi"
              cpu: "250m"
          ports:
            - containerPort: 5000
```
`kubectl apply -f d_kubernetes.yaml` ile deployment oluşturulur

## LoadBalancer Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-api-service
spec:
  type: LoadBalancer
  selector:
    app: flask-api
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
```
`kubectl apply -f s_kubernetes_loadbalancer.yaml` ile servis oluşturulur

## LoadBalancer servis üzerinden erişim 

###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-lzqvs Hostip: 10.1.0.241
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-vq74t Hostip: 10.1.0.239
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-h48zg Hostip: 10.1.0.240
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-vq74t Hostip: 10.1.0.239
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-h48zg Hostip: 10.1.0.240
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-h48zg Hostip: 10.1.0.240
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-lzqvs Hostip: 10.1.0.241
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-vq74t Hostip: 10.1.0.239
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-lzqvs Hostip: 10.1.0.241
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-vq74t Hostip: 10.1.0.239

## Ölçeklendirme

`kubectl scale deployment/flask-api-deployment --replicas 5` ile replika sayısı istenildiği gibi ayarlanabilir

###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-h48zg Hostip: 10.1.0.240
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-h48zg Hostip: 10.1.0.240
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-zxhz5 Hostip: 10.1.0.243
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-sfs7j Hostip: 10.1.0.242
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-sfs7j Hostip: 10.1.0.242
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-lzqvs Hostip: 10.1.0.241
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-zxhz5 Hostip: 10.1.0.243
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-lzqvs Hostip: 10.1.0.241
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-zxhz5 Hostip: 10.1.0.243
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-h48zg Hostip: 10.1.0.240
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-vq74t Hostip: 10.1.0.239
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-lzqvs Hostip: 10.1.0.241
###### curl localhost:5000
##### Hostname: flask-api-deployment-5b684b857b-vq74t Hostip: 10.1.0.239