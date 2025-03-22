# import scipy.io as sio
# import torch
#
# mat_data = sio.loadmat('../val.mat')
# f = mat_data['features']
# a = torch.tensor(f).double()
# print(f)
import kagglehub

# Download latest version
path = kagglehub.dataset_download("huangxian11111111/1111111")

print("Path to dataset files:", path)
