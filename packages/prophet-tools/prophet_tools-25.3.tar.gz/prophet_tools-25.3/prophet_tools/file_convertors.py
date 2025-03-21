from os import remove
from PIL import Image
from prophet_tools.file_info import files_list
from prophet_tools.my_functions import check_in, check_ends_with, get_filename_from_whole_path
from prophet_tools.terminal import print_in_color

def _resize_one_image(image, lim):
    width, height = image.size
    if width < lim and height < lim:
        return image
    ratio = width/height
    if width > height:
        width = lim
        height = int(width/ratio)
    else:
        height = lim
        width = int(height*ratio)

    new_image = image.resize((width, height))
    return new_image

def convert_CR2_to_JPG(path_from, path_to, resize_limit=2500):
    image = Image.open(path_from)
    width, height = image.size
    rgb_image = image.convert('RGB')
    rgb_image.resize((width, height))
    new_image = _resize_one_image(rgb_image, resize_limit)
    new_image.save(path_to)

def image_resizer(path, size=2500):
    def resize_image_max(path, lim):
        image = Image.open(path)
        new_image = _resize_one_image(image, lim)
        image.close()
        if path[-4:] == 'webp':
            path = path[:-4] + 'jpg'
        new_image.save(path)
        return path

    def batch_image_resizer(files, lim=2500):
        print_in_color(f"Resizing started ({lim})", orange=True)
        delete_these_images = []
        for img_path in files:
            new_path = img_path
            image = Image.open(img_path)
            width, height = image.size
            img_name = get_filename_from_whole_path(img_path)
            max_w_h = max(width, height)

            if max_w_h > lim:
                new_path = resize_image_max(img_path, lim)
                print_in_color(img_name, green=True)
            else:
                if check_ends_with(img_path, ['webp']):
                    new_path = resize_image_max(img_path, max_w_h)
                    print_in_color(img_name, blue=True)

            if img_path != new_path:
                delete_these_images.append(img_path)

        print_in_color("All resized", yellow=True)
        return delete_these_images

    files = files_list(path)
    files_to_resize = []
    for file in files:
        if check_in(file.ext, ['jpg', 'jpeg', 'png', 'webp']):
            files_to_resize.append(file.path)
        if check_in(file.ext, 'avif'):
            print_in_color(f'найден avif файл --- {file.folder_name} \ {file.name}', red=True, style='b')
    delete_these_images = batch_image_resizer(files_to_resize, lim=size)
    for image in delete_these_images:
        remove(image)




if __name__ == '__main__':
    size = input("MAX SIZE OR FOLDER: ")
    # size = r'C:\Users\ProPHet\Pictures\пережатие'
    if size.isnumeric():
        size = int(size)
        path = input("Ссылка на папку: ")
    else:
        path = size
        size = 2500


    # path = r'C:\Users\ProPHet\Pictures\пережатие'
    # size = 3000
    image_resizer(path, size)