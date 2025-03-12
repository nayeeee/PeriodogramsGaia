import ray

# Inicia Ray
#resources={'num_cpus': 16}
ray.init()

@ray.remote
def hello_world():
    return "Hola, Mundo!"

# Llama a la función remota
result = ray.get(hello_world.remote())
print(result)
print(ray.cluster_resources())

# Cierra Ray
ray.shutdown()