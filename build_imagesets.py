# Copyright 2017 Taylor H. Paul (taylorpaul2011@gmail.com) All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Divides a directory of files in to train/validation/test sets.

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

"""
import os, random
from sys import argv
import ntpath
import math
import shutil

#List of subdirs that will be created in dirname
SUBDIRS=["train", "validation", "test"]

def _file_count(dirname):

  """
  Count the files in each sub-directory and return

  Args:
    dirname: string, path to a data set directory, e.g.,
    '/path/to/images'

  Returns:
    count_dictionary: dictionary of file counts in sub-directories
  """

  count_dictionary={}
  labeled_list=[] #Track which labels already counted, so to not count duplicates in SUBDIRS twice

  for root, dirs, files in os.walk(dirname):
    # print(root)
    if root == dirname:
      target_dirs= [d for d in dirs if d not in SUBDIRS]
      print("target_dirs: ", target_dirs)
    if ntpath.basename(root) in target_dirs and ntpath.basename(root) not in labeled_list:
      count_dictionary[root]=len(files)
      labeled_list.append(ntpath.basename(root))
    else:
      print("!!!!!!  Warning, only counted and sorted first level of subdirectories: \n ", target_dirs, "\n", root, "Directory Not Counted !!!!!!")

  return count_dictionary


def _choose_files(dirname, count_dict, dir_percentages=[80,10,10]):

  """
  Randomly choose a percentage of files from multiple sub-directories of dirname (str) variable.

  Args:
    dirname: string, path to a data set directory, e.g.,
      '/path/to/images'
    dir_percentages: List of sub-set percentages of available images,
      e.g., [train%, validation%, test%].
    count_dict: a dictionary in format
      count_dict["PATH to Label_Dir"] = num_files_in_dir (int)

  Returns:
    Array of three lists containing filenames from subdirectories for moving images to their new sub-set.

    result = [[training_file_list],
                [validation_file_list],
                [test_file_list]]
  """
  file_set_dict={}

  #Multiply by percentage to get total number of selection for each test_file_list
  for key in sorted(count_dict):
    train_count = math.ceil(dir_percentages[0]/100 * count_dict[key])
    validation_count= math.floor(dir_percentages[1]/100  * count_dict[key])
    test_count = count_dict[key] - train_count - validation_count
  #Test print statements
    # print("Train Count: \n",train_count)
    # print("Valid Count: \n",validation_count)
    # print("Test Count: \n",test_count)

    #Choose the files:

    #Pickout enough files for the validation and test set:
    valid_test_list= random.sample(os.listdir(key), (validation_count+test_count))

    #Pickout files for the test_list:
    test_list = random.sample(valid_test_list, test_count)

    #Get not used files from valid_test_list for validation_list:
    validation_list=[f for f in valid_test_list if f not in test_list]



    #Finally pick remaining files for training set:
    train_list = [f for f in os.listdir(key) if f not in valid_test_list]

    #Uncomment to check error checker is working:
    # validation_list.append(test_list[0])

    #Be sure there is not common items!
    check1=set(test_list).intersection(validation_list)
    check2=set(train_list).intersection(valid_test_list)
    if (check1 or check2):
      print("Error: ", check1, check2, "exists in both test and validation set!!!")

    #Save variables to dictionary:
    file_set_dict[key] = [train_list, validation_list, test_list]

    #Check that no files were lost:
    if count_dict[key] == (len(file_set_dict[key][0])+len(file_set_dict[key][1])+ len(file_set_dict[key][2])):
      print("Train, test, validation lists length check PASS! No files lost from ", key)

  return file_set_dict


def _make_dirs(dirname, dir_percentages, label_dirs):
  """
  Creates 2 or 3 sub-directories in dirname to create folders for the train, validation, and test sets if a percentage was allocated for each in set_percentages.

  Args:
    dirname: string, path to a data set directory, e.g.,
      '/path/to/images'
    dir_percentages: List of sub-set percentages of available images,
      e.g., [train%, validation%, test%].

  Returns:
    Nothing, but dirname directory will have new files:

      dirname/train
      dirname/validation
      dirname/test

  """

  if dir_percentages[0]:
    train_dir=os.path.join(dirname, "train")
    os.makedirs(train_dir, exist_ok=True)
    print("Created Directory: ", train_dir)
  if dir_percentages[1]:
    valid_dir=os.path.join(dirname, "validation")
    os.makedirs(valid_dir, exist_ok=True)
    print("Created Directory: ", valid_dir)
  if dir_percentages[2]:
    test_dir=os.path.join(dirname, "test")
    os.makedirs(test_dir, exist_ok=True)
    print("Created Directory: ", test_dir)

  dir_list = [train_dir, valid_dir, test_dir]

  #Make a new label directory in each train, validation, and test directory:
  for d in dir_list:
    for label_path in label_dirs:

      #Make the dir by joining d with just the actual label of each label path:
      label_dir=os.path.join(d, ntpath.basename(label_path))
      os.makedirs(label_dir, exist_ok=True)
      print("Created Directory: ", label_dir)

  return dir_list


def _move_files(original_dirs, new_dirs, file_list_dict):
  """
  Move files in file_list_dict from original_dirs to new_dirs to divide files into train, validation and test sets.

  Args:
    dirname: string, path to a data set directory, e.g.,
      '/path/to/images'
    dir_percentages: List of sub-set percentages of available images,
      e.g., [train%, validation%, test%].

  Returns:
    Nothing, but new_dirs will now posses new files:

      dirname/train/label1/movedfile1train.foo
      dirname/train/label2/movedfile2train.foo

      dirname/validation/label1/movedfile1valid.foo
      dirname/validation/label2/modevedfile2valid.foo

      dirname/test ... same format as above
  """

  for key in file_list_dict:
    #Move Training Images from other and screenshot:
    train_count=0
    for train_file in file_list_dict[key][0]:
      train_dest = os.path.join(new_dirs[0], ntpath.basename(key)+ "\\" + train_file)
      shutil.move(os.path.join(key, train_file), train_dest)
      train_count +=1

    print( train_count, " files moved to ", train_dest )

    #Move Validation Images from other and screenshot:
    valid_count=0
    for valid_file in file_list_dict[key][1]:
      valid_dest = os.path.join(new_dirs[1], ntpath.basename(key)+ "\\" + valid_file)
      shutil.move(os.path.join(key, valid_file), valid_dest)
      valid_count += 1

    print( valid_count, " files moved to ", valid_dest )

    #Move Test Images from other and screenshot:
    test_count = 0
    for test_file in file_list_dict[key][2]:
      test_dest = os.path.join(new_dirs[2], ntpath.basename(key)+ "\\" + test_file)
      shutil.move(os.path.join(key, test_file), test_dest)
      test_count += 1

    print( test_count, " files moved to ", test_dest )

    #Remove the now empty directory:
    try:
      os.rmdir(key)
    except OSError as ex:
      if ex.errno == errno.ENOTEMPTY:
        print (key, "directory not empty when tried to delete after moves!!!")

  return


def main(dirname, set_percentages=[90,10,0]):

  #Get a count of the files in the sub-directories of dirname:
  file_count_dict = _file_count(dirname)
  print(file_count_dict)
  # Let the user know what files you found and store valid directories for use in _move_files():
  key_list=[]
  for key in file_count_dict:
    print("From ", key, "found this many files: ", file_count_dict[key])
    if ntpath.basename(key) not in SUBDIRS:
        key_list.append(key)
    print(key_list)

  #From the files found, develop train, validation, and test lists:
  file_list_dict = _choose_files(dirname, file_count_dict)

  #Make required new directories:
  new_dirs = _make_dirs(dirname, set_percentages, key_list)

  #Move the files form dirname sub-directories to appropriate set directories:
  _move_files(key_list, new_dirs, file_list_dict)

  #Create label.txt file:
  labelfile = open(os.path.join(dirname, "label.txt"), 'w')
  for label in key_list:
    labelfile.write("%s\n" % ntpath.basename(label))

  print ("File containing all labels located in ", labelfile.name)

  return 0

if __name__ == '__main__':
  dirname = argv[1]
  if argv[2]:
    set_percentages = argv[2]
  else:
    set_percentages = [90,10,0]
  main(dirname, set_percentages)
