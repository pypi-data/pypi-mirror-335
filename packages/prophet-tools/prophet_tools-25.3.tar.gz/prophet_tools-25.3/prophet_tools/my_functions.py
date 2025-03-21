import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)
from auto_import import import_or_install

# python3 -m pip install --upgrade Pillow
def ppath_replace_slahses(ppath):
    return ppath.replace("\\",r"/")

def write_to_file(filename, txt):
    if type(txt) is list:
        txt2 = ''
        for line in txt:
            txt2 += line + '\n'
        txt = txt2

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(txt)

def read_from_file(filename, split_to_lines=False):
    with open(filename, 'r', encoding='utf-8') as file:
        txt = file.read()
    if split_to_lines:
        return txt.splitlines()
    return txt

def list_of_files(ppath,scan_subfolders=False) -> list:
    def getting_files(tt,i):
        tmp = tt[i][2]
        for f in tmp:
            folder_path = ppath_replace_slahses(tt[i][0])
            files.append(f"{folder_path}/{f}")

    import os
    t = os.walk(ppath)
    tt = list(t)
    if tt == []:
        print("Function 'list_of_files' returned ERROR: No such folder")
    else:
        files = []
        if scan_subfolders == True:
            for i in range(0,len(tt)):
                getting_files(tt,i)
        else:
            i = 0
            getting_files(tt,i)

        return files

def get_filename_from_whole_path(path):
    if r'/' in path:
        return path.split(r'/')[-1]
    return path.split('\\')[-1]

def split_filename_to_name_and_ext(file):
    extention = '.' + file.split('.')[-1]
    name = file[:len(extention) * -1]
    return name, extention

def ffmpeg_merge_files(video_source,audio_source):
    import subprocess    
    import os
    output_source = video_source + "merged.mp4"
    print('=== ffmpeg merging')
    subprocess.run(f"C:/ffmpeg.exe -i {video_source} -i {audio_source} -c copy {output_source}")
    os.remove(video_source)
    os.remove(audio_source)
    os.rename(output_source, video_source)
    print('=== ffmpeg merge complete')

def save_file_from_URL(direct_link, filename):
    from urllib import request
    request.urlretrieve(direct_link, filename)

def get_from_URL(URL,save_to_response_page=False):
    import_or_install('requests')
    import requests

    # URL = 'https://www.google.ru/'
    response = requests.get(URL)
    txt = response.text
    txt = txt.replace("\\u0026","&")
    if save_to_response_page ==True:
        with open("C:/Users/user/Downloads/_Удалить/response page.html", 'wb') as ffile:
            ffile.write(txt.encode("utf-8"))
    # print("Код ответа: " + str(response.status_code))
    return txt

def replace_banned_symbols(txt,new_chr='_'):
    txt = txt.replace(chr(60),new_chr) # <
    txt = txt.replace(chr(62),new_chr) # >
    txt = txt.replace(chr(58),new_chr) # :
    txt = txt.replace(chr(34),new_chr) # "
    txt = txt.replace(chr(47),new_chr) # /
    txt = txt.replace(chr(92),new_chr) # \
    txt = txt.replace(chr(124),new_chr) # |
    txt = txt.replace(chr(63),new_chr) # ?
    txt = txt.replace(chr(42),new_chr) # *
    return txt

def replace_part_of_string(text,replacement,position,eend):
    result = text[:position] + replacement + text[position + (eend-position):]
    return result

def read_txt_as_dict(ppath):
    result = {}
    res_list = []
    with open(ppath) as f:
        txt = f.read()
        if txt[-1] == "\n":
            txt = txt[0:-1]
        lines = txt.split('>')

        if txt.count("<") == 0:
            result = lines
        else:
            for line in lines:
                if line.count('>') == 1:
                    (key, val) = line.split('<')
                    result[key] = val
                else:
                    res_list.append(line.split('<'))
    if len(result) > 1:
        return result
    else:
        return res_list

def extract_filename_extention(ppath):
    s = ppath.split('.')
    return '.' + s[-1]

def get_property_from_file(filename, prop):
    from os.path import getmtime
    from datetime import datetime


    if prop == 'mod_time':
        return datetime.fromtimestamp(getmtime(filename))

def list_of_folders_with_full_path(ppath, subfolders=False, debug=False):
    import os
    all_folders = []
    if debug:
        print(ppath)
    all_files_and_folders = list(os.walk(ppath))
    if len(all_files_and_folders) == 0:
        return []
    folders = all_files_and_folders[0][1]
    if len(folders) == 0:
        return []
    for folder in folders:
        all_folders.append(f'{ppath}\\{folder}')
    if subfolders:
        for folder in folders:
            new_folders = list_of_folders_with_full_path(f'{ppath}\\{folder}', subfolders=subfolders, debug=debug)
            all_folders.extend(new_folders)
    return all_folders

def list_of_folders(ppath, subfolders=False, debug=False):
    import os
    if debug:
        print(ppath)
    all_files_and_folders = list(os.walk(ppath))
    if len(all_files_and_folders) == 0:
        return []
    folders = all_files_and_folders[0][1]
    if len(folders) == 0:
        return []
    all_folders = folders.copy()
    if subfolders:
        for folder in folders:
            new_folders = list_of_folders(f'{ppath}/{folder}', subfolders=subfolders, debug=debug)
            all_folders.extend(new_folders)
    return all_folders

def copy_to_clipboard(txt):
    import_or_install('pyperclip')
    from pyperclip import copy as cb_copy
    cb_copy(txt)

def get_from_clipboard():
    import_or_install('pyperclip')
    from pyperclip import paste as cb_paste
    return cb_paste()

def get_all_drives_names():
    import os.path
    dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)]
    return drives

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def open_folder_in_explorer(folder):
    import os
    folder = folder.replace('/', '\\')
    os.popen(f'explorer {folder}')

def clear_case(what):
    if type(what) is str:
        what = what.lower()
    if type(what) is list:
        what = what.copy()
        for i in range(len(what)):
            what.insert(i, what.pop(i).lower())
    return what

def check_in(what, where, ignore_case=False):
    if what == '' or where == '':
        return False
    if ignore_case:
        what = clear_case(what)
        where = clear_case(where)
    if type(what) is type(where) is str:
        return what in where or where in what
    elif type(what) is str:
        for place in where:
            if what in place:
                return True
    elif type(where) is str:
        for thing in what:
            if thing in where:
                return True
    elif type(what) is type(where) is list:
        for thing in what:
            for place in where:
                if thing in place:
                    return True
    return False

def check_ends_with(what, where, ignore_case=False):
    if what == '' or where == '':
        return False
    if ignore_case:
        what = clear_case(what)
        where = clear_case(where)

    if type(what) is type(where) is str:
        return what.endswith(where)

    if type(what) is not str and type(where) is not str:
        for wha in what:
            for whe in where:
                if wha.endswith(whe):
                    return True
    elif type(what) is not str:
        for wha in what:
            if wha.endswith(where):
                return True
    elif type(where) is not str:
        for whe in where:
            if what.endswith(whe):
                return True
    return False

def check_starts_with(what, where, ignore_case=False):
    if what == '' or where == '':
        return False
    if ignore_case:
        what = clear_case(what)
        where = clear_case(where)

    if type(what) is type(where) is str:
        return what.startswith(where)

    if type(what) is not str and type(where) is not str:
        for wha in what:
            for whe in where:
                if wha.startswith(whe):
                    return True
    elif type(what) is not str:
        for wha in what:
            if wha.startswith(where):
                return True
    elif type(where) is not str:
        for whe in where:
            if what.startswith(whe):
                return True
    return False


def delete_trailing_spaces(txt):
    while txt[0] == ' ':
        txt = txt[1:]
    while txt[-1] == ' ':
        txt = txt[:-1]
    return txt



def convert_link_to_filename(link):
    start = link.find('://') + 3
    name = link[start:]
    name = name.replace('/', "_")
    return name

if __name__ == '__main__':
    print(check_ends_with('C:\\Users\\ProPHet\\Pictures\\пережатие\\1896205816629f8ee1d12786.96956893.webp', ['.webp']))