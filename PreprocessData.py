import pickle

import cv2
import numpy as np
import matplotlib.pyplot as plt
import random


# a method to load a pickle file
def unpickle(file):
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict


# load train, test, and meta
print("Loading Data..")

train_dec = unpickle('./cifar-100-python/train')
test_dec = unpickle('./cifar-100-python/test')
meta = unpickle('./cifar-100-python/meta')


# a method to convert to grayscale
def rgb2gray(dataset):
    return np.dot(np.array(dataset, dtype='float32'), [0.299, 0.587, 0.114])


# a method to sharpen the blurry images
def sharpen(dataset):
    # img = rgb2gray(img)
    kernel = (-1 / 256.0) * np.array(
        np.asarray([[1, 4, 6, 4, 1], [4, 16, 24, 16, 4], [6, 24, -476, 24, 6], [4, 16, 24, 16, 4], [1, 4, 6, 4, 1]]))

    for i in range(dataset.shape[0]):
        dataset[i] = cv2.filter2D(dataset[i], -1, kernel)

    return dataset


# a method to return dataset in format [num_images,image_height,image_width,num_channels]
def reshape(dataset):
    return np.reshape(dataset, (-1, 3, 32, 32)).transpose((0, 2, 3, 1))


# a method to shuffle dataset and labels
def randomize(dataset, labels):
    permutation = np.random.permutation(dataset.shape[0])
    shuffled_dataset = dataset[permutation, :, :]
    shuffled_labels = labels[permutation]
    return shuffled_dataset, shuffled_labels


# a method to display and save a sample of the images
def disp_sample_dataset(dataset, label, label_names, cmap=None):
    items = random.sample(range(dataset.shape[0]), 8)
    for i, item in enumerate(items):
        plt.subplot(2, 4, i + 1)
        plt.axis('off')
        plt.title(label_names[label[i]])
        plt.imshow(dataset[i, :, :], cmap=cmap, interpolation='none')
    plt.savefig('./output_images/plt.png')
    plt.show()


# load data and labels
train_data = train_dec[b'data']
train_labels = np.array(train_dec[b'fine_labels'])
test_data = test_dec[b'data']
test_labels = np.array(test_dec[b'fine_labels'])
label_names = meta[b'fine_label_names']

# reshape and shuffle
print("Shuffling Data..")

train_data = reshape(train_data)
test_data = reshape(test_data)
train_data, train_labels = randomize(train_data, train_labels)
# test_data, test_labels = randomize(test_data, test_labels)

# normalize
print("Sharpening Data..")
disp_sample_dataset(train_data, train_labels, label_names)

train_data = sharpen(train_data)
test_data = sharpen(test_data)
disp_sample_dataset(train_data, train_labels, label_names)


# a method to take some images as a validation set
def get_valid_set(dataset, labels, count_per_class=20, num_classes=100):
    counter = np.zeros((num_classes), dtype='int32')
    valid_size = count_per_class * num_classes
    valid_dataset = np.zeros((valid_size, 32, 32, 3), dtype='float32')
    valid_labels = np.zeros((valid_size), dtype='int32')

    valid_index = 0
    for i in range(dataset.shape[0]):
        if labels[i] >= count_per_class:
            continue
        valid_dataset[valid_index] = dataset[i]
        valid_labels[valid_index] = labels[i]
        valid_index = valid_index + 1
        counter[labels[i]] = counter[labels[i]] + 1
        if (valid_index == valid_size):
            break

    return valid_dataset, valid_labels


print("Pickling Normalized Data..")

# valid_data, valid_labels = get_valid_set(test_data, test_labels)

pickle_file = 'CIFAR_100_processed.pickle'

# pickle data after pre processing
try:
    f = open(pickle_file, 'wb')
    save = {
        'train_dataset': train_data,
        'train_labels': train_labels,
        'test_dataset': test_data,
        'test_labels': test_labels,
        'label_names': label_names
    }
    pickle.dump(save, f, pickle.HIGHEST_PROTOCOL)
    f.close()
    print("Done")
except Exception as e:
    print('Unable to save data to', pickle_file, ':', e)
    raise
