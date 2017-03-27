Find the original repo here: https://github.com/tensorflow/models/tree/master/tutorials/image/cifar10

Forked only the CIFAR-10 directory to complete the tutorial and make the exercise changes.

## Added files:

This section briefly describes the files I added in order to use the cifar10 network on my own image set.

### build_imagesets.py

Divides a directory of files in to train/validation/test sets.

The data set is expected to reside in files located in the
following directory structure.

  data_dir/label_0/image0.jpeg
  data_dir/label_0/image1.jpg
  ...
  data_dir/label_1/weird-image.jpeg
  data_dir/label_1/my-image.jpeg
  ...

where the sub-directory is the unique label associated with these files.

This script is intended to be used for an already downloaded image set which will be prepared and further processed using build_image_data.py from:

https://github.com/tensorflow/models/tree/master/inception/inception/data



-----------------------Original README-----------------------------------

CIFAR-10 is a common benchmark in machine learning for image recognition.

http://www.cs.toronto.edu/~kriz/cifar.html

Code in this directory demonstrates how to use TensorFlow to train and evaluate a convolutional neural network (CNN) on both CPU and GPU. We also demonstrate how to train a CNN over multiple GPUs.

Detailed instructions on how to get started available at:

http://tensorflow.org/tutorials/deep_cnn/
