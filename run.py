"""
This script implements a simple image hashing pipeline:
    1. Create a db containing hashes for the given dataset
    2. Given a query image, provide a list of images with similar hash values

Note:
    * A trivial hashing method called dhash will be used to generate the hashes for given image.
    * This script was tested with Caltech_101 dataset.
"""

import os
import argparse
import shelve
import glob
import cv2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create', action='store_true',
            help='Create hash db')
    parser.add_argument('-d', '--dataset', type=str,
            help='Directory containing images')
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

def create_hashes_db(datadir, dbname):
    # Open db
    if os.path.isfile(dbname):
        os.remove(dbname)
    db = shelve.open(dbname, writeback=True)

    # Extract hash for each image and store it in db 
    imagepaths = glob.glob('{}/*/*.jpg'.format(datadir))
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

def main():
    # Parse args
    args = parse_args()
    
    # Create hash db
    if args.create:
        create_hashes_db(args.dataset, args.shelve)

if __name__=='__main__':
    main()
