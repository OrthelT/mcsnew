import os
import argparse

def clean_file_names(directory):
    for file in os.listdir(directory):
        if file.endswith('.xlsx') or file.endswith('.txt') or file.endswith('.pdf'):
            new_name = file.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            os.rename(os.path.join(directory, file), os.path.join(directory, new_name))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Clean file names in a directory', 
        epilog="""
        Example:
        clean_file_names.py data/feb26/ 
        """)
    parser.add_argument('directory', type=str, help='The directory with files to clean')
    args = parser.parse_args()
    directory = args.directory
    clean_file_names(directory)
    print(f"Cleaned file names in {directory}")
else:
    print("This module is not meant to be imported")
