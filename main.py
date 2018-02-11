"""
This script implements a simple image hashing pipeline:
    1. Create a db containing hashes for the given dataset
    2. Given a query image, provide a list of images with similar hash values

Note:
    * A trivial hashing method called dhash will be used to generate the hashes for given image.
    * This script was tested with Caltech_101 dataset.
"""

import os
import random
import argparse
import shelve
import glob
import cv2
from collections import OrderedDict

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create', action='store_true',
            help='Create hash db')
    parser.add_argument('--query', action='store_true',
            help='Find similar images related to query image')
    parser.add_argument('-t', '--trainfile', type=str,
            help='File containing training images')
    parser.add_argument('-e', '--evalfile', type=str,
            help='File containing eval images')
    parser.add_argument('-s', '--shelve', type=str, required=True,
            help='Database containing hashes')
    return parser.parse_args()

def dhash(image, hashsize=8):
    '''Taken from https://github.com/JohannesBuchner/imagehash'''
    # Resize it to 9 x 8 
    image = cv2.resize(image, (hashsize+1, hashsize))
    # Find relative differences
    diff = image[:, 1:] > image[:, :-1]
    # Convert to bit string
    diff = diff.flatten().astype(int)
    diff_bin = ''.join([str(b) for b in diff])
    # Convert to hex
    width = len(diff_bin)/4
    return '{:0>{width}x}'.format(int(diff_bin, 2), width=width)

def extract_lines_from_file(fname):
    f = open(fname, 'r')
    lines = [line.rstrip('\n') for line in f.readlines()]
    f.close()
    return lines

def create_hashes_db(trainfile, dbname):
    # Open db
    if os.path.isfile(dbname):
        os.remove(dbname)
    db = shelve.open(dbname, writeback=True)

    # Extract hash for each image and store it in db
    imagepaths = extract_lines_from_file(trainfile)
    num_images = len(imagepaths)
    for i, imagepath in enumerate(imagepaths):
        # Read grayscale image
        image = cv2.imread(imagepath, cv2.IMREAD_GRAYSCALE)

        # Compute hash value
        hashval = dhash(image)
        
        # Store hash value to db
        db.setdefault(hashval, []).append(imagepath)

        print 'Extracted hashes for {}/{} images\r'.format(i+1, num_images)

    print 'Total hashes stored : {}'.format(len(db.keys()))
    db.close()

def hamming_distance(hash1, hash2):
    d = 0
    for c1, c2 in zip(hash1, hash2):
        if c1 != c2:
            d += 1
    return d

def test(evalfile, dbname):
    """A random image from test list will be used for testing"""
    # Parse test images path
    imagepaths = extract_lines_from_file(evalfile)

    # Randomly select a image
    imagepath = random.choice(imagepaths)

    # Read image
    image = cv2.imread(imagepath, cv2.IMREAD_GRAYSCALE)
    
    # Compute hash
    hash1 = dhash(image)

    # Compare Hamming distance
    db = shelve.open(dbname)
    print 'Searching...'
    matches = {}
    for key in db.keys():
        d = hamming_distance(hash1, key)
        if d < 10:
            matches.setdefault(d, []).append(db[key])

    macthes = OrderedDict(sorted(matches.items()))
    print 'Found matches : {}'.format(len(matches))
    # Save images
    query = cv2.imread(imagepath)
    cv2.imwrite('Query.jpg', query)
    n = 0
    for i, d in enumerate(matches.keys()):
        for match in matches[d]:
            for m in match:
                if n == 10: # Limit search to 10 items
                    break
                image = cv2.imread(m, cv2.IMREAD_COLOR)
                cv2.imwrite('Match_{}_d_{}.jpg'.format(i+1, d), image)
                n += 1

def main():
    # Parse args
    args = parse_args()
    
    # Create hash db
    if args.create:
        create_hashes_db(args.trainfile, args.shelve)

    # Query given image
    elif args.query:
        test(args.evalfile, args.shelve)

if __name__=='__main__':
    main()
