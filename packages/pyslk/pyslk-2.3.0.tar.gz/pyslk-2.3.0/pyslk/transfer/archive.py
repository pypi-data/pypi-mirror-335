import glob
from os import path as op

from ..raw import archive_raw

__all__ = [
    "archive",
]


def archive(
    resource, dst_gns, recursive=False, retry=False, **kwargs
) -> tuple[list, str]:
    """Upload data to tape archive using slk archive

    This archiving function wraps some functionalities around :py:meth:`~pyslk.archive_raw`.
    It returns a list of archived files or directories and can use
    `tenacity <https://github.com/jd/tenacity>`_ for retrying failed archive attempts.

    :param resource:
        Path, pattern or list of files that should be archived.
    :type resource: ``str`` or ``list``
    :param dst_gns:
        Destination directory for archiving.
    :type dst_gns: ``str``
    :param recursive:
        Archive recursively.
    :type recursive: ``bool``
    :param retry:
        Retry archiving if an ``ArchiveError`` is encountered.
        If ``retry`` is True and archiving fails due to ``ArchiveError``,
        archiving will wait for 10 seconds and retry. Maximal 3 attempts are made.
        After that, ``ArchiveError`` will be raised after all.
        Requires ``tenacity`` to be installed.
    :type retry: ``bool``
    :returns:
        a tuple containing archived files and stdout from archive_raw.
    :rtype: ``(list, str)``

    .. seealso::
        * :py:meth:`~pyslk.archive_raw`

    """

    if not isinstance(resource, type([])):
        resource = [resource]

    resources = []
    for r in resource:
        resources.extend(map(op.abspath, glob.glob(r)))

    # remove possible duplicates
    resources = list(dict.fromkeys(resources))
    # create paths of archived files for return
    arch_file_paths = [op.join(dst_gns, op.basename(r)) for r in resources]

    if retry is True:
        from ..retry import try_archive

        return arch_file_paths, try_archive(
            resources, dst_gns, recursive=recursive, **kwargs
        )
    return arch_file_paths, archive_raw(
        resources, dst_gns, recursive=recursive, **kwargs
    )
