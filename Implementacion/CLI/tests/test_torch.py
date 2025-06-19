import torch, torchvision
print(f"PyTorch: {torch.__version__}")
print(f"Torchvision: {torchvision.__version__}")
print(f"¿CUDA disponible?: {torch.cuda.is_available()}")
print(f"Versión CUDA: {torch.version.cuda}")