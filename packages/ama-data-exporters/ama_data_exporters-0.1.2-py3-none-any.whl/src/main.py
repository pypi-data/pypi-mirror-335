import src.dataloaders as dataloader

print("Modules in dataloader:", dataloader.__all__)

# Accessing imported modules
for module_name in dataloader.__all__:
    module = getattr(dataloader, module_name)
    print(f"Module {module_name}: {module}")
