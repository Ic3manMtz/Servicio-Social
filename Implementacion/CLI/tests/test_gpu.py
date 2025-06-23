import torch

if torch.cuda.is_available():
    print("¡CUDA funciona correctamente!")
    print(f"Dispositivo: {torch.cuda.get_device_name(0)}")
else:
    print("ERROR: No se detectó GPU/CUDA")
    print("Posibles causas:")
    print("1. Fallo en el mapeo de dispositivos")
    print("2. Versiones incompatibles de drivers/CUDA")
    print("3. Falta de librerías en el contenedor")