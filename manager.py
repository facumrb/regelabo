import docker
client = docker.from_env()

def create_student(nombre):
    container = client.containers.run(
        "cc3d-laboratorio-virtual:latest",
        detach=True,
        name=f"lab_{nombre}",
        labels={
            "traefik.enable": "true",
            f"traefik.http.routers.{nombre}.rule": f"Host(`{nombre}.laboratorio.local`)"
        },
        volumes={f'./proyectos/{nombre}': {'bind': '/home/cc3d/proyectos', 'mode': 'rw'}},
        shm_size='512m'
    )
    return f"Laboratorio para {nombre} creado en http://{nombre}.laboratorio.local"

# Aquí podrías añadir una interfaz con Flask o FastAPI para el login