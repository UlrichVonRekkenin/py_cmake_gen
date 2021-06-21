import os
import argparse
import re
from xml.dom.minidom import parse

CMAKE_SEP = '/'


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--entry', required=True, type=str, help='File with main() entry point function.')
    parser.add_argument('--dirs', required=True, type=str, help='Comma separated list of folders for look up.')
    parser.add_argument('-o', required=True, type=str, help='Generated filename')
    parser.add_argument('--prefix', type=str, help='The prefix for FILES and FILES_INCLUDE_DIRS cmake variables.')
    parser.add_argument('--excludes', type=str, help='Comma separated list of base filename to exclude.')

    return parser.parse_known_args()[0]


def get_file_list(directory_list, mask=('.h', '.cpp', '.ui'), excludes=()):
    return [os.path.abspath(f'{root}{os.path.sep}{file}') for lookup in directory_list \
            for root, dir_list, file_list in os.walk(lookup) \
            for file in [f for f in file_list if os.path.splitext(f)[1] in mask] \
            if os.path.splitext(os.path.basename(file))[0] not in excludes]


def get_includes_in_file(file):
    def __pure(line):
        return line.replace('#include ', '').replace('\n', '').replace('"', '').lstrip().rstrip()

    ext = os.path.splitext(file)[1]

    if ext in ['.h', '.cpp']:
        return [__pure(line) for line in open(file, 'r', encoding='utf-8').readlines() \
                if '#include "' in line and not line.strip().startswith(r"//")]
    elif ext in ['.ui']:
        return [os.path.basename(h.firstChild.data) for h in parse(file).getElementsByTagName("header")]


def get_path_by_name(name, include_list):
    def __name(file):
        return os.path.splitext(os.path.basename(file))[0]

    return [x for x in include_list if __name(name) == __name(x)]


def get_all_necessary_files(include_list, file_list):
    return [item for sublist in [get_path_by_name(file, file_list) for file in include_list] for item in sublist]


def find_in_file(root, file_list):
    global includes
    tmp = get_all_necessary_files(get_includes_in_file(root), file_list)
    if len(tmp):
        for i in [i for i in tmp if i not in includes]:
            includes.append(i)
            find_in_file(i, file_list)

    return includes


def pattern_matching(file):
    main = re.compile(r"int\smain\(int.\w*,\schar\*\s\w*\[\]\)$")
    qttest = re.compile(r"QTEST\w*_MAIN\(\w*\)$")
    return any(main.match(line) or qttest.match(line) for line in open(file, 'r', encoding='utf-8').readlines())


argv = args()
entry, output = argv.entry, argv.o
directories = list(map(os.path.abspath, argv.dirs.split(',')))
files = get_file_list(directories, excludes=argv.excludes if argv.excludes is not None else ())
prefix = (argv.prefix + "_" if argv.prefix is not None else "").upper()
includes = []

if not pattern_matching(entry):
    print(f'It seems like file {entry} does not have appropriate entry (main or QtTest)')

if not os.path.exists(os.path.dirname(output)):
    os.mkdir(os.path.dirname(output))

with open(output, 'w', encoding='utf-8') as f:
    needed = sorted(list(set([entry] + find_in_file(entry, files))))
    f.write(f"# This file was generated automatically\n# Do not edit this one\n\nset({prefix}FILES\n")
    [f.write("\t\t{}\n".format(file.replace("\\", CMAKE_SEP))) for file in needed]
    f.write(")\n\n")

    f.write(f"set({prefix}INCLUDE_DIRS\n")
    [f.write("\t\t{}\n".format(d.replace("\\", CMAKE_SEP))) for d in directories]
    f.write(")\n")
