import torch

load_path = './epoch_500_model.pt'
ckpt = torch.load(load_path, map_location='cpu')
model.load_state_dict(ckpt['state_dict'])
model = model.to('cuda')
model.eval()