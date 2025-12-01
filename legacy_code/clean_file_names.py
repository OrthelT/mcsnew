import os

def clean_file_names(directory):
    for file in os.listdir(directory):
        if file.endswith('.xlsx') or file.endswith('.txt'):
            new_name = file.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            os.rename(os.path.join(directory, file), os.path.join(directory, new_name))

if __name__ == '__main__':
    directory = 'data'
    clean_file_names(directory)
    print(f"Cleaned file names in {directory}")
else:
    print("This module is not meant to be imported")
