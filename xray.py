import dataclasses
import itertools
import ntpath
import os
import sys

from typing import List, Dict

FileName = str
FolderName = str

def partition(pred, iterable):
    'Use a predicate to partition entries into false entries and true entries'
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = itertools.tee(iterable)
    return itertools.filterfalse(pred, t1), filter(pred, t2)

@dataclasses.dataclass
class FileMeta(object):
    name: str
    size: int

    @classmethod
    def from_path(cls, path):
        name = ntpath.basename(path)
        size = os.path.getsize(path)
        return FileMeta(name, size)


@dataclasses.dataclass
class FolderMeta(object):
    name: str
    files_meta: Dict[FileName, FileMeta]
    folders_meta: Dict[FolderName, 'FolderMeta']
    size: int
    files_count: int
    folders_count: int


def explore_path(path: str) -> FolderMeta:
    entity_names = os.listdir(path)
    paths = (os.path.join(path, name) for name in entity_names)
    folder_paths, file_paths = partition(os.path.isfile, paths)
    files_meta = (FileMeta.from_path(path) for path in file_paths)
    subfolders_meta = (explore_path(path) for path in folder_paths)

    folder_name = ntpath.basename(path)
    
    files_meta = {meta.name: meta for meta in files_meta}
    files_size = sum(meta.size for meta in files_meta.values())
    folders_meta = {meta.name: meta for meta in subfolders_meta}
    folders_size = sum(meta.size for meta in folders_meta.values())

    files_count = len(files_meta) + sum(meta.files_count
                                        for meta in folders_meta.values())
    folders_count = len(folders_meta) + sum(meta.folders_count
                                            for meta in folders_meta.values())

    return FolderMeta(folder_name,
                      files_meta,
                      folders_meta,
                      files_size + folders_size,
                      files_count,
                      folders_count)

def main(argv):
    print(explore_path(argv[1]).size >> 20)


if __name__ == "__main__":
    sys.exit(main(sys.argv))