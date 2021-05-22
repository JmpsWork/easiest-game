"""Used for getting all the keys and file paths for images"""
import os

allowed_formats = ['jpg', 'png', 'bmp', 'gif']
os.chdir('.')


def get_images() -> dict:

    all_images = {}
    for root, dirs, files in os.walk('images'):
        for file_name in files:
            file_path = f'{root}/{file_name}'.replace('\\', '/')
            key = '/'.join(file_path.split('/')[1:])
            key, file_format = key.split('.')
            if file_format in allowed_formats:
                all_images[key] = file_path
                print(f'Loaded {file_path} as {key}')
    return all_images
