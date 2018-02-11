"""
Script for generating train/test indices
"""

import os
import glob
import random
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', type=str, required=True,
            help='Path of Dataset directory')
    return parser.parse_args()

def write_to_file(fname, lines):
    f = open(fname, 'w')
    for line in lines:
        f.write('{}\n'.format(line))
    f.close()

def generate_indices_files(dataset_dir):
    # Get list of all images
    images = glob.glob('{}/*/*.jpg'.format(dataset_dir))

    # Shuffle randomly
    random.shuffle(images)

    # Split into train/test
    split_idx = int(0.95 * len(images))
    train = images[:split_idx]
    test = images[split_idx:]

    # Write to files
    write_to_file('train.txt', train)
    write_to_file('test.txt', test)

    print 'Generated train.txt and test.txt files'

def main():
    # Parse args
    args = parse_args()

    # Generate train and test indices file
    generate_indices_files(args.dataset)
    

if __name__=='__main__':
    main()
