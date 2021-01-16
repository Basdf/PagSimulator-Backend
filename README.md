# PagSimulator-Backend

Backend para la aplicacion final de la materia sistemas operativos y laboratirio.
La aplicaciones permite simular las diferentes politicas de paginacion de un sistema operativo.

## Despliegue local
Ejecutar el siguiente comando en la consola "uvicorn main:app --reload".

## Despliegue con docker
Para el despliegue con docker, ejecutar el sigueinte comando en la consola "docker-compose up --build -d", se creara el contenero y la api estara expuesta en el puerto 8000.
En la ruta "http://localhost:8000/docs" se encontrara la documentacion de la api.

## Heroku
La aplicacion tambien se encuentra alojada en Heroku "https://pag-simulator-backend.herokuapp.com/", la documentacion de la api se encuentra en la ruta "https://pag-simulator-backend.herokuapp.com/docs".


