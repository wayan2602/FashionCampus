# -*- coding: utf-8 -*-
"""Untitled13.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11KenKlqtrPPu-k5nzWISVhjjFERaTC1U
"""

import requests
from PIL import Image
from io import BytesIO
import numpy
import matplotlib.pyplot as plt
import pandas as pd

image_paths = "/content/drive/MyDrive/Dataset HD/bag-hd-dataset/bag (102).png"

img = Image.open(image_paths).convert(mode="L")
img = img.resize((28, 28))
# img = img * 255
x = (255 - numpy.expand_dims(numpy.array(img), -1))

from google.colab import drive
drive.mount('/content/drive')

plt.imshow(x.squeeze ( - 1), cmap="gray")

np_imge = numpy.array(x.squeeze ( - 1))
print(np_imge)

#Cuma buat ngetest hasil arraynya
data = Image.fromarray(np_imge)
      

data.save('testing result.png')

#rubah array jadi csv
#save csv
data = np_imge.tofile('data102.csv', sep = ',')
# df = pd.read_csv('data1.csv')
# df