import os

def get_files_by_extension_single_dir(directory_path, extension):
    files_with_extension = []
    for filename in os.listdir(directory_path):
        if filename.endswith(extension) and os.path.isfile(os.path.join(directory_path, filename)):
            files_with_extension.append(os.path.join(directory_path, filename))
    return files_with_extension