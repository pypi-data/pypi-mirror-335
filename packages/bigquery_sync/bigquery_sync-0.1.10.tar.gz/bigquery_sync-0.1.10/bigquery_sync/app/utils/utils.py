import re
import os
import sys


def format_snake_case(filename):
    tmp1 = re.sub('[^\w,^\s]', '', filename)  # only character number and underscore and space
    tmp2 = re.sub(' +', '_', tmp1)  # replace space to _
    return re.sub('_+', '_', tmp2).lower()  # replace multiple _ to one _


def save_number(matched):
    return str(matched[1])


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


COLOR_PREFIXES = {'r': '\33[31m', 'g': '\33[32m'}
COLOR_SUFFIX = '\33[0m'


def get_colored_string(color, msg):
    support_color = False
    if color is not None:
        plat = sys.platform
        supported_platform = (plat != 'Pocket PC') and \
                             (plat != 'win32' or 'ANSICON' in os.environ)
        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        support_color = supported_platform and is_a_tty

    if support_color:
        return COLOR_PREFIXES[color] + msg + COLOR_SUFFIX
    else:
        return msg


def get_dependency_views_dict(diff_file_status_dict, check_status):

    def get_dependency(query):
        dependency_views = []
        for file_path, status in diff_file_status_dict.items():
            if status in check_status and os.path.splitext(file_path)[1] == '.sql':
                project, dataset, view = file_path.split('/')[-3:]
                view = os.path.splitext(view)[0]
                if re.search(r'(`?{}?`?.?)?`?{}`?.`?{}`?'.format(project, dataset, view), query):
                    dependency_views.append(file_path)
        return dependency_views

    dependency_views_dict = {}
    for file_path, status in diff_file_status_dict.items():
        if status in check_status and os.path.splitext(file_path)[1] == '.sql':
            with open(file_path, 'r') as sql_file:
                query = sql_file.read()
            dependency_views_dict[file_path] = [p for p in get_dependency(query=query) if p != file_path]

    return dependency_views_dict
