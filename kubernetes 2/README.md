# 2

- [2](#2)
  - [Docker](#docker)
    - [Ayağa kaldırılacak olan uygulama app.py](#ayağa-kaldırılacak-olan-uygulama-apppy)
    - [Uygulamanın Dockerfile'ı requirements.txt içine uygulamanın bağımlılığı olan Flask yazılarak hazırlanır](#uygulamanın-dockerfileı-requirementstxt-içine-uygulamanın-bağımlılığı-olan-flask-yazılarak-hazırlanır)
    - [Versiyon 1 için docker-compose-v1.yml](#versiyon-1-için-docker-compose-v1yml)
    - [Versiyon 2 için docker-compose-v2.yml](#versiyon-2-için-docker-compose-v2yml)
    - [`docker images` komutu ile benzer bir çıktı alınmalıdır](#docker-images-komutu-ile-benzer-bir-çıktı-alınmalıdır)
  - [Deployment](#deployment)
    - [d\_kubernetes\_cluster\_v1.yaml](#d_kubernetes_cluster_v1yaml)
    - [d\_kubernetes\_cluster\_v2.yaml](#d_kubernetes_cluster_v2yaml)
  - [Erişim için servislerin oluşturulması](#erişim-için-servislerin-oluşturulması)
    - [s\_kubernetes\_cluster\_v1.yaml](#s_kubernetes_cluster_v1yaml)
    - [s\_kubernetes\_cluster\_v2.yaml](#s_kubernetes_cluster_v2yaml)
  - [Servisler ClusterIP türünden olduğu için pod'lara bağlanılarak test edilebilir](#servisler-clusterip-türünden-olduğu-için-podlara-bağlanılarak-test-edilebilir)

## Docker
### Ayağa kaldırılacak olan uygulama app.py

```python
from flask import Flask
import os
import socket

app = Flask(__name__)


@app.route('/')
def hello_world():
    version = os.getenv("VERSION")
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    # Hangi namespace altındaki hangi pod'un çalıştığının dönmesi için
    return f'version: {version} Hostname: {host_name} Hostip: {host_ip} \n'


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

### Versiyon 1 için docker-compose-v1.yml
```yml
version: '3'
services:
  s_flask_api:
    image: web-app:v1
    container_name: c_flask_api_v1
    build: .
    ports:
      - "5000:5000"
```

```bash
docker-compose -f docker-compose-v1.yml  build
```

### Versiyon 2 için docker-compose-v2.yml
```yml
version: '3'
services:
  s_flask_api:
    image: web-app:v2
    container_name: c_flask_api_v2
    build: .
    ports:
      - "5000:5000"
```

```bash
docker-compose -f docker-compose-v2.yml  build
```

### `docker images` komutu ile benzer bir çıktı alınmalıdır

| REPOSITORY |  TAG  |   IMAGE ID   |    CREATED    |    SIZE |
| :--------- | :---: | :----------: | :-----------: | ------: |
| web-app    |  v1   | 295c75bd7a48 | 2 minutes ago | 1.01 GB |
| web-app    |  v2   | 295c75bd7a48 | 2 minutes ago | 1.01 GB |

## Deployment

### d_kubernetes_cluster_v1.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-api-deployment-v1
  namespace: v1
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
          image: web-app:v1
          ports:
            - containerPort: 5000
          env:
            - name: VERSION
              value: v1
```
### d_kubernetes_cluster_v2.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-api-deployment-v2
  namespace: v2
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
          image: web-app:v2
          ports:
            - containerPort: 5000
          env:
            - name: VERSION
              value: v2
```
> Deployment dosyalarında uygulamaların yalıtılması için namespace'ler v1 ve v2 şeklinde belirtilir ayrıca uygulamada belirtilen VERSION environment'ının değerleri de belirtilir.

`kubectl create namespace v1` ve `kubectl create namespace v2` komutlarıyla namespace'ler oluşturulur

`kubectl apply -f d_kubernetes_cluster_v1.yaml` ve `kubectl apply -f d_kubernetes_cluster_v2.yaml` komutları ile deployment'lar oluşturulur.

`kubectl get deployments -n v1`

| NAME                    | READY | UP-TO-DATE | AVAILABLE |  AGE |
| :---------------------- | :---: | :--------: | :-------: | ---: |
| flask-api-deployment-v1 |  3/3  |     3      |     3     |  67s |

`kubectl get deployments -n v2`

| NAME                    | READY | UP-TO-DATE | AVAILABLE |  AGE |
| :---------------------- | :---: | :--------: | :-------: | ---: |
| flask-api-deployment-v2 |  3/3  |     3      |     3     |  68s |

`kubectl get pods -n v1`
| NAME                                     | READY | STATUS  | RESTARTS |  AGE |
| :--------------------------------------- | :---: | :-----: | :------: | ---: |
| flask-api-deployment-v1-759ff56d5f-gbndm |  1/1  | Running |    0     |   5m |
| flask-api-deployment-v1-759ff56d5f-krvdg |  1/1  | Running |    0     |   5m |
| flask-api-deployment-v1-759ff56d5f-md5bx |  1/1  | Running |    0     |   5m |

`kubectl get pods -n v2`
| NAME                                     | READY | STATUS  | RESTARTS |  AGE |
| :--------------------------------------- | :---: | :-----: | :------: | ---: |
| flask-api-deployment-v2-6c9f896c79-94rlh |  1/1  | Running |    0     |   5m |
| flask-api-deployment-v2-6c9f896c79-9qt9v |  1/1  | Running |    0     |   5m |
| flask-api-deployment-v2-6c9f896c79-ws6ql |  1/1  | Running |    0     |   5m |

benzeri çıktılar elde edilmelidir.

## Erişim için servislerin oluşturulması

### s_kubernetes_cluster_v1.yaml 

```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-api-service-v1
  namespace: v1
spec:
  type: ClusterIP
  selector:
    app: flask-api
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
```

### s_kubernetes_cluster_v2.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-api-service-v2
  namespace: v2
spec:
  type: ClusterIP
  selector:
    app: flask-api
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
```

Servislerde de deployment'lara benzer şekilde namespace'ler belirtilir

`kubectl apply -f s_kubernetes_cluster_v1.yaml` 
`kubectl get services -n v1`

| NAME                 |   TYPE    |  CLUSTER-IP   | EXTERNAL-IP | PORT(S)  |  AGE |
| :------------------- | :-------: | :-----------: | :---------: | :------: | ---: |
| flask-api-service-v1 | ClusterIP | 10.105.195.38 |   <none>    | 5000/TCP |  26s |

`kubectl apply -f s_kubernetes_cluster_v2.yaml`
`kubectl get services -n v2`

| NAME                 |   TYPE    |  CLUSTER-IP   | EXTERNAL-IP | PORT(S)  |  AGE |
| :------------------- | :-------: | :-----------: | :---------: | :------: | ---: |
| flask-api-service-v2 | ClusterIP | 10.108.47.251 |   <none>    | 5000/TCP |  24s |

## Servisler ClusterIP türünden olduğu için pod'lara bağlanılarak test edilebilir

`kubectl exec flask-api-deployment-v1-759ff56d5f-gbndm -it bash -n v1`

###### root@flask-api-deployment-v1-759ff56d5f-gbndm:/app# curl flask-api-service-v1:5000
##### version: v1 Hostname: flask-api-deployment-v1-759ff56d5f-gbndm Hostip: 10.1.0.210
###### root@flask-api-deployment-v1-759ff56d5f-gbndm:/app# curl flask-api-service-v1:5000
##### version: v1 Hostname: flask-api-deployment-v1-759ff56d5f-md5bx Hostip: 10.1.0.209
###### root@flask-api-deployment-v1-759ff56d5f-gbndm:/app# curl flask-api-service-v1:5000
##### version: v1 Hostname: flask-api-deployment-v1-759ff56d5f-md5bx Hostip: 10.1.0.209
###### root@flask-api-deployment-v1-759ff56d5f-gbndm:/app# curl flask-api-service-v1:5000
##### version: v1 Hostname: flask-api-deployment-v1-759ff56d5f-gbndm Hostip: 10.1.0.210
###### root@flask-api-deployment-v1-759ff56d5f-gbndm:/app# curl flask-api-service-v1:5000
##### version: v1 Hostname: flask-api-deployment-v1-759ff56d5f-gbndm Hostip: 10.1.0.210
###### root@flask-api-deployment-v1-759ff56d5f-gbndm:/app# curl flask-api-service-v1:5000
##### version: v1 Hostname: flask-api-deployment-v1-759ff56d5f-md5bx Hostip: 10.1.0.209
###### root@flask-api-deployment-v1-759ff56d5f-gbndm:/app# curl flask-api-service-v1:5000
##### version: v1 Hostname: flask-api-deployment-v1-759ff56d5f-md5bx Hostip: 10.1.0.209
###### root@flask-api-deployment-v1-759ff56d5f-gbndm:/app# curl flask-api-service-v1:5000
##### version: v1 Hostname: flask-api-deployment-v1-759ff56d5f-krvdg Hostip: 10.1.0.208

 `kubectl exec flask-api-deployment-v2-6c9f896c79-94rlh -it bash -n v2`
 
###### root@flask-api-deployment-v2-6c9f896c79-94rlh:/app# curl flask-api-service-v2:5000
##### version: v2 Hostname: flask-api-deployment-v2-6c9f896c79-ws6ql Hostip: 10.1.0.212
###### root@flask-api-deployment-v2-6c9f896c79-94rlh:/app# curl flask-api-service-v2:5000
##### version: v2 Hostname: flask-api-deployment-v2-6c9f896c79-94rlh Hostip: 10.1.0.213
###### root@flask-api-deployment-v2-6c9f896c79-94rlh:/app# curl flask-api-service-v2:5000
##### version: v2 Hostname: flask-api-deployment-v2-6c9f896c79-94rlh Hostip: 10.1.0.213
###### root@flask-api-deployment-v2-6c9f896c79-94rlh:/app# curl flask-api-service-v2:5000
##### version: v2 Hostname: flask-api-deployment-v2-6c9f896c79-94rlh Hostip: 10.1.0.213
###### root@flask-api-deployment-v2-6c9f896c79-94rlh:/app# curl flask-api-service-v2:5000
##### version: v2 Hostname: flask-api-deployment-v2-6c9f896c79-ws6ql Hostip: 10.1.0.212
###### root@flask-api-deployment-v2-6c9f896c79-94rlh:/app# curl flask-api-service-v2:5000
##### version: v2 Hostname: flask-api-deployment-v2-6c9f896c79-9qt9v Hostip: 10.1.0.211
###### root@flask-api-deployment-v2-6c9f896c79-94rlh:/app# curl flask-api-service-v2:5000
##### version: v2 Hostname: flask-api-deployment-v2-6c9f896c79-94rlh Hostip: 10.1.0.213
###### root@flask-api-deployment-v2-6c9f896c79-94rlh:/app# curl flask-api-service-v2:5000
##### version: v2 Hostname: flask-api-deployment-v2-6c9f896c79-ws6ql Hostip: 10.1.0.212
