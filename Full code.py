# -*- coding: utf-8 -*-
"""LAST ROMUSA - Astungkare Mesari

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BFIStV9q2gRWebFv4qZ6BGPGSU-VF6Wg
"""

import torch, torchvision
from torch import nn
from torch import optim
from torchvision.transforms import ToTensor
import torch.nn.functional as F
import matplotlib.pyplot as plt

import requests
from PIL import Image
from io import BytesIO

from sklearn.metrics import confusion_matrix
from torch.nn import Linear, ReLU, CrossEntropyLoss, Sequential, Conv2d, MaxPool2d, Module, Softmax, BatchNorm2d, Dropout

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize

from sklearn.metrics import accuracy_score, roc_auc_score, roc_curve, confusion_matrix

from torchvision import transforms

from sklearn.model_selection import train_test_split

from torch.utils.data import DataLoader,Dataset,ConcatDataset

from skimage.io import imread
from skimage.transform import resize
from skimage.util import invert

"""##Getting Data"""

from google.colab import drive
drive.mount('/content/drive')

train_data = pd.read_csv("/content/drive/MyDrive/dataset/train_data.csv")
test_data = pd.read_csv("/content/drive/MyDrive/dataset/test_data.csv")
df = pd.concat([train_data, test_data], sort=False)
# display(train[0:5])
# display(test[0:5])

df.shape

y = df['label'].values
X = df.drop(['label'],1).values


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

print(y_test.shape)

BATCH_SIZE = 64
torch_X_train = torch.from_numpy(X_train).type(torch.LongTensor)
torch_y_train = torch.from_numpy(y_train).type(torch.LongTensor) # data type is long

# create feature and targets tensor for test set.
torch_X_test = torch.from_numpy(X_test).type(torch.LongTensor)
torch_y_test = torch.from_numpy(y_test).type(torch.LongTensor) # data type is long

torch_X_train = torch_X_train.view(-1, 1,28,28).float()
torch_X_test = torch_X_test.view(-1,1,28,28).float()
print(torch_X_train.shape)
print(torch_X_test.shape)



# Pytorch train and test sets
train = torch.utils.data.TensorDataset(torch_X_train,torch_y_train)

test = torch.utils.data.TensorDataset(torch_X_test,torch_y_test)

# data loader
train_loader = torch.utils.data.DataLoader(train, batch_size = BATCH_SIZE, shuffle = False)
test_loader = torch.utils.data.DataLoader(test, batch_size = BATCH_SIZE, shuffle = False)

mean = [0.2812668149052327]
std = [0.349463855153678]



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

TT = transform=transforms.Compose([
                      # transforms.ToPILImage(),
                      transforms.RandomHorizontalFlip(),
                      transforms.RandomVerticalFlip(),
                      transforms.RandomRotation(15),
                      transforms.RandomRotation([90, 180]),
                      transforms.Resize([28, 28]),
                      transforms.RandomCrop([28, 28]),
                      transforms.ToTensor(),
                      transforms.Normalize(torch.Tensor(mean), torch.Tensor(std))
                      ])






T = transforms.Compose([
    # transforms.ToPILImage(),
    transforms.ToTensor(),
    transforms.Normalize(torch.Tensor(mean), torch.Tensor(std))
    ])



"""##Creating Model"""

class Net1(nn.Module):

    def __init__(self):
        super().__init__()

        self.fc1 = nn.Linear(784,256)
        self.fc2 = nn.Linear(256,128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64,11)

        self.dropout = nn.Dropout(0.2)
        

    def forward(self, x):
        # one activated conv layer
        x = x.view(x.shape[0], -1)
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.dropout(F.relu(self.fc2(x)))
        x = self.dropout(F.relu(self.fc3(x)))
        x = F.log_softmax(self.fc4(x), dim=1)

        return x
cnn = Net1()

n_epochs = 3
batch_size_train = 64
batch_size_test = 1000
learning_rate = 0.01
momentum = 0.5
log_interval = 10

random_seed = 1
torch.backends.cudnn.enabled = False
torch.manual_seed(random_seed)

network = Net1()
optimizer = optim.SGD(network.parameters(), lr=0.001,
                      momentum=0.9)

train_losses = []
train_counter = []
test_losses = []
test_counter = [i*len(train_loader.dataset) for i in range(n_epochs + 1)]

def train(epoch):
  network.train()
  for batch_idx, (data, target) in enumerate(train_loader):
    optimizer.zero_grad()
    output = network(data)
    loss = F.nll_loss(output, target)
    loss.backward()
    optimizer.step()
    if batch_idx % log_interval == 0:
      print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
        epoch, batch_idx * len(data), len(train_loader.dataset),
        100. * batch_idx / len(train_loader), loss.item()))
      train_losses.append(loss.item())
      train_counter.append(
        (batch_idx*64) + ((epoch-1)*len(train_loader.dataset)))
      torch.save(network.state_dict(), '/content/drive/MyDrive/model/modelfix.pth')
      torch.save(optimizer.state_dict(), '/content/drive/MyDrive/model/optimizerfix.pth')

def test():
  network.eval()
  test_loss = 0
  correct = 0
  with torch.no_grad():
    for data, target in test_loader:
      output = network(data)
      test_loss += F.nll_loss(output, target, size_average=False).item()
      pred = output.data.max(1, keepdim=True)[1]
      correct += pred.eq(target.data.view_as(pred)).sum()
  test_loss /= len(test_loader.dataset)
  test_losses.append(test_loss)
  print('\nTest set: Avg. loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
    test_loss, correct, len(test_loader.dataset),
    100. * correct / len(test_loader.dataset)))

test()
for epoch in range(1, n_epochs + 1):
  train(epoch)
  test()

examples = enumerate(test_loader)
batch_idx, (example_data, example_targets) = next(examples)

with torch.no_grad():
  output = network(example_data)

fig = plt.figure()
for i in range(6):
  plt.subplot(2,3,i+1)
  plt.tight_layout()
  plt.imshow(example_data[i][0], cmap='gray', interpolation='none')
  plt.title("Prediction: {}".format(
    output.data.max(1, keepdim=True)[1][i].item()))
  plt.xticks([])
  plt.yticks([])
fig



continued_network = Net1()
continued_optimizer = optim.SGD(continued_network.parameters(), lr=0.001,
                                momentum=0.9)

network_state_dict = torch.load("/content/drive/MyDrive/model/modelfix.pth")
continued_network.load_state_dict(network_state_dict)

optimizer_state_dict = torch.load("/content/drive/MyDrive/model/optimizerfix.pth")
continued_optimizer.load_state_dict(optimizer_state_dict)

for i in range(4,20):
  test_counter.append(i*len(train_loader.dataset))
  train(i)
  test()

with torch.no_grad():
  output1 = continued_network(example_data)

# for i in range(20):
#   print("{}".format(output1.data.max(1, keepdim=True)[1][i].item()))
fig = plt.figure()
for i in range(6):
  plt.subplot(2,3,i+1)
  plt.tight_layout()
  plt.imshow(example_data[i][0], cmap='gray', interpolation='none')
  plt.title("Prediction: {}".format(
    output.data.max(1, keepdim=True)[1][i].item()))
  plt.xticks([])
  plt.yticks([])
fig

fig = plt.figure()
plt.plot(train_counter, train_losses, color='blue')
plt.scatter(test_counter, test_losses, color='red')
plt.legend(['Train Loss', 'Test Loss'], loc='upper right')
plt.xlabel('number of training examples seen')
plt.ylabel('negative log likelihood loss')
fig

"""##Validation Function"""

def predict_dl(model, data):
    y_pred = []
    y_true = []
    for i, (images, labels) in enumerate(data):
        images = images
        x = model(images)
        value, pred = torch.max(x, 1)
        pred = pred.data
        y_pred.extend(list(pred.numpy()))
        y_true.extend(list(labels.numpy()))
    return np.array(y_pred), np.array(y_true)

y_pred, y_true = predict_dl(continued_network, test_loader)

"""##Confusion Matrix"""

pd.DataFrame(confusion_matrix(y_true, y_pred, labels=np.arange(0,11)))

"""##Interference Function

##Predict Data Result
"""

def view_classify(img, ps):
    ''' Function for viewing an image and it's predicted classes.
    '''
    ps = ps.data.numpy().squeeze()

    fig, (ax1, ax2) = plt.subplots(figsize=(6,9), ncols=2)
    ax1.imshow(img.resize_(1, 28, 28).numpy().squeeze(), cmap='gray')
    ax1.axis('off')
    ax2.barh(np.arange(11), ps)
    ax2.set_aspect(0.1)
    ax2.set_yticks(np.arange(11))
    ax2.set_yticklabels(np.arange(11))
    ax2.set_yticklabels(['T-shirt/top',
                        'Trouser',
                        'Pullover',
                        'Dress',
                        'Coat',
                        'Sandal',
                        'Shirt',
                        'Sneaker',
                        'Bag',
                        'Ankle Boot',
                        'hat'], size='small');
    ax2.set_title('Class Probability')
    ax2.set_xlim(0, 1.1)

    plt.tight_layout()

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
def make_prediction(data):
    images, labels = next(iter(data))
    image_index = 34
    img = images[image_index].view(1, 784)
    # Turn off gradients to speed up this part
    with torch.no_grad():
        logps = continued_network(img)


    

    # Output of the network are log-probabilities, need to take exponential for probabilities
    ps = torch.exp(logps)
    view_classify(img.view(1, 28, 28), ps)
make_prediction(test_loader)

classes = [
    "T-shirt/Top",
    "Trouser",
    "Pullover",
    "Dress",
    "Coat",
    "Sandal",
    "Shirt",
    "Sneaker",
    "Bag",
    "Ankle Boat",
    "Hat",
]

model = Net1()
continued_optimizer = optim.SGD(model.parameters(), lr=0.001,
                                momentum=0.5)

network_state_dict = torch.load("/content/drive/MyDrive/model/modelfix.pth")
model.load_state_dict(network_state_dict)

optimizer_state_dict = torch.load("/content/drive/MyDrive/model/optimizerfix.pth")
continued_optimizer.load_state_dict(optimizer_state_dict)

mean = [0.2859]
std = [0.3530]



image_transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize(torch.Tensor(mean), torch.Tensor(std))
])

def classify(model,image_transform, image_path, classes):
  model = model.eval()
  image = Image.open(image_path).convert('L')
  image = image.resize((28, 28))
  image = image_transform(image).float()
  image = image.unsqueeze(axis=0)

  output = model(image)
  _, predicted = torch.max(output, 1)
  print(classes[predicted.item()])

image_paths = "/content/drive/MyDrive/jury/Copy of mnist_358.png"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')

image_paths = "/content/drive/MyDrive/jury/Copy of mnist_58.png"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')

image_paths = "/content/drive/MyDrive/jury/Copy of mnist_11_shoes.png"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')

image_paths = "/content/drive/MyDrive/jury/Copy of mnist_41.png"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')

image_paths = "/content/drive/MyDrive/jury/Copy of mnist_35_bag.png"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')

image_paths = "/content/drive/MyDrive/jury/Copy of sandal_1.jpeg"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')

image_paths = "/content/drive/MyDrive/jury/Copy of mnist_112.png"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')

image_paths = "/content/drive/MyDrive/jury/Copy of hat_3.jpg"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')

image_paths = "/content/drive/MyDrive/jury/Copy of hat_4.jpg"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')

image_paths = "/content/drive/MyDrive/jury/Copy of trouser_1.jpg"
classify(model, image_transform, image_paths, classes)
image = Image.open(image_paths)
plt.imshow(image, cmap='gray')