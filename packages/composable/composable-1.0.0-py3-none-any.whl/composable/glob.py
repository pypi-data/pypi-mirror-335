from .pipeable import pipeable
import glob as g

@pipeable
def glob(pathname, *, recursive=False):
    '''Return a possibly empty list of path names that match pathname, which must be a string containing a path specification. pathname can be either absolute (like /usr/src/Python-1.5/Makefile) or relative (like ../../Tools/*/*.gif), and can contain shell-style wildcards. Broken symlinks are included in the results (as in the shell). Whether or not the results are sorted depends on the file system. If a file that satisfies conditions is removed or added during the call of this function, whether a path name for that file be included is unspecified.

    If root_dir is not None, it should be a path-like object specifying the root directory for searching. It has the same effect on glob() as changing the current directory before calling it. If pathname is relative, the result will contain paths relative to root_dir.

    This function can support paths relative to directory descriptors with the dir_fd parameter.

    If recursive is true, the pattern “**” will match any files and zero or more directories, subdirectories and symbolic links to directories. If the pattern is followed by an os.sep or os.altsep then files will not match.

    If include_hidden is true, “**” pattern will match hidden directories.
    '''
    return g.glob(pathname, recursive=recursive)