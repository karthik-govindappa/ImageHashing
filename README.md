# ImageHashing
A simple Image Hashing script to get the gist of the concept

## Generate indices files
Download Caltech dataset from [Caltech_101](http://www.vision.caltech.edu/Image_Datasets/Caltech101/)

` python indices.py -d ~/datasets/Caltech_101`

## Train
`python main.py --create --trainfile=train.txt --shelve=db.shelve`

## Test
`python main.py --evalfile=test.txt --shelve=db.shelve --query`
