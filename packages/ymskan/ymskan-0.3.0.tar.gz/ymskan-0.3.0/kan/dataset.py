import scipy.io as sio
import torch
from torch.utils.data import Dataset, DataLoader


class KanDataset(Dataset):
    def __init__(self, data_path):
        self.path = data_path
        self.data = sio.loadmat(data_path)
        self.features = torch.tensor(self.data['features']).double()
        self.labels = torch.tensor(self.data['labels'].squeeze()).double()

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        feature = self.features[idx]
        label = self.labels[idx]
        return feature, label


if __name__ == '__main__':
    dataset = KanDataset(r'D:\Code\2-ZSL\Zero-Shot-Learning\data\新建文件夹\1\val.mat')
    print(dataset.__len__())
    data_loader = DataLoader(dataset=dataset, batch_size=2, shuffle=True)
    for data, label in data_loader:
        print(label.shape)
