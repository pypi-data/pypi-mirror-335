"""Based on https://src.fedoraproject.org/rpms/python-cryptography/blob/rawhide/f/vendor_rust.py"""

import os
import pathlib
import stat
import tarfile


def _tar_reset(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
    """Reset user, group, mtime, and mode to create reproducible tar"""
    tarinfo.uid = 0
    tarinfo.gid = 0
    tarinfo.uname = "root"
    tarinfo.gname = "root"
    tarinfo.mtime = 0
    if tarinfo.type == tarfile.DIRTYPE or stat.S_IMODE(tarinfo.mode) & stat.S_IXUSR:
        tarinfo.mode = 0o755
    else:
        tarinfo.mode = 0o644
    if tarinfo.pax_headers:
        raise ValueError(tarinfo.name, tarinfo.pax_headers)
    return tarinfo


def tar_reproducible(
    tar: tarfile.TarFile,
    basedir: pathlib.Path,
    prefix: pathlib.Path | None = None,
) -> None:
    """Create reproducible tar file

    Add content from basedir to already opened tar. If prefix is provided, use
    it to set relative paths for the content being added.

    """

    content = [str(basedir)]  # convert from pathlib.Path, if that's what we have
    for root, dirs, files in os.walk(basedir):
        for directory in dirs:
            content.append(os.path.join(root, directory))
        for filename in files:
            content.append(os.path.join(root, filename))
    content.sort()

    for fn in content:
        # Ensure that the paths in the tarfile are rooted at the prefix
        # directory, if we have one.
        arcname = fn if prefix is None else os.path.relpath(fn, prefix)
        tar.add(fn, filter=_tar_reset, recursive=False, arcname=arcname)
