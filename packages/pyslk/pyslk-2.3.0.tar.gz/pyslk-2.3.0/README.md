# pyslk README

This is a python wrapper library for `slk` and `slk_helpers`. The `slk` is the official command line interface of StrongLink (R) by Crystal Onyx, which is the software managing the tape archive at DKRZ (Deutsches Klimarechenzentrum / German Climate Computing Center). `slk_helpers` are an in-house development of DKRZ which extends `slk`. This wrapper is compatible with slk versions `>= 3.3.76` (`>= 3.3.90` recommended) and slk helpers versions `>= 1.13.0` (`>= 1.13.3` recommended).

If you have any questions, please contact support@dkrz.de .


## Installation

### Dependencies

The installation requires the following dependencies

* `>= python 3.9`
* `>= slk 3.3.76` (`>= slk 3.3.90` recommended)
* `>= slk_helpers 1.13.0` (`>= slk_helpers 1.13.3` recommended)
* `>= pandas 1.4.0`
* `psutil`
* `>= python-dateutil 2.8.2`
* `>= tenacity 8.0.1`


### Installatin via pip

The package can be installed via pip:

```console
pip install pyslk
```

If a specific version is required:

```console
pip install pyslk=2.2.9
```

### Installation with conda/mamba

You can also install `pyslk` into a conda environment:

```console
mamba create -n slk pip
conda activate slk
```

download the latest release for your Python version from one of these locations:

* https://gitlab.dkrz.de/hsm-tools/pyslk/-/packages
* https://hsm-tools.gitlab-pages.dkrz.de/pyslk/availability.html#conda-packages

Install the package es follows (example for pyslk 2.2.4):

```console
conda install --use-local  pyslk-2.2.4-py_0.conda`
```


## Usage

All command lines arguments of `slk` v3.3.91 and `slk_helpers` v1.13.3 are available as the functions' arguments.

A few basic usage examples:

### List files

```python
# load library
> import pyslk
> import os
# list content of a folder
> pyslk.list("/arch/bm0146/k204221/iow")
    permissions    owner   group      filesize       date   time                                    filename
0   -rwxr-xr-x-  k204221  bm0146  1.268945e+06 2020-06-10  08:25          /arch/bm0146/k204221/iow/INDEX.txt
1   -rw-r--r--t  k204221  bm0146  2.094216e+10 2020-06-05  17:36  /arch/bm0146/k204221/iow/iow_data2_001.tar
2   -rw-r--r--t  k204221  bm0146  2.034971e+10 2020-06-05  17:38  /arch/bm0146/k204221/iow/iow_data2_002.tar
3   -rw-r--r--t  k204221  bm0146  2.088344e+10 2020-06-05  17:38  /arch/bm0146/k204221/iow/iow_data2_003.tar
4   -rw-r--r--t  k204221  bm0146  2.071567e+10 2020-06-05  17:40  /arch/bm0146/k204221/iow/iow_data2_004.tar
5   -rw-r--r--t  k204221  bm0146  2.047869e+10 2020-06-05  17:40  /arch/bm0146/k204221/iow/iow_data2_005.tar
6   -rw-r--r--t  k204221  bm0146  8.364491e+09 2020-06-05  17:41  /arch/bm0146/k204221/iow/iow_data2_006.tar
7   -rw-r--r--t  k204221  bm0146  2.007016e+11 2020-06-05  19:37  /arch/bm0146/k204221/iow/iow_data3_001.tar
8   -rw-r--r--t  k204221  bm0146  2.646606e+10 2020-06-05  19:14  /arch/bm0146/k204221/iow/iow_data3_002.tar
9   -rw-r--r--t  k204221  bm0146  4.194304e+06 2020-06-05  19:43  /arch/bm0146/k204221/iow/iow_data4_001.tar
10  -rw-r--r--t  k204221  bm0146  1.128477e+10 2020-06-05  19:46  /arch/bm0146/k204221/iow/iow_data4_002.tar
11  -rw-r--r--t  k204221  bm0146  2.094216e+10 2020-06-10  08:21  /arch/bm0146/k204221/iow/iow_data5_001.tar
12  -rw-r--r--t  k204221  bm0146  2.034971e+10 2020-06-10  08:23  /arch/bm0146/k204221/iow/iow_data5_002.tar
13  -rw-r--r--t  k204221  bm0146  2.088344e+10 2020-06-10  08:23  /arch/bm0146/k204221/iow/iow_data5_003.tar
14  -rw-r--r--t  k204221  bm0146  2.071567e+10 2020-06-10  08:24  /arch/bm0146/k204221/iow/iow_data5_004.tar
15  -rw-r--r--t  k204221  bm0146  2.047869e+10 2020-06-10  08:25  /arch/bm0146/k204221/iow/iow_data5_005.tar
16  -rw-r--r--t  k204221  bm0146  8.364491e+09 2020-06-10  08:25  /arch/bm0146/k204221/iow/iow_data5_006.tar
17  -rw-r--r--t  k204221  bm0146  2.094216e+10 2020-06-05  17:53   /arch/bm0146/k204221/iow/iow_data_001.tar
18  -rw-r--r--t  k204221  bm0146  2.034971e+10 2020-06-05  17:53   /arch/bm0146/k204221/iow/iow_data_002.tar
19  -rw-r--r--t  k204221  bm0146  2.088344e+10 2020-06-05  17:56   /arch/bm0146/k204221/iow/iow_data_003.tar
20  -rw-r--r--t  k204221  bm0146  2.071567e+10 2020-06-05  17:56   /arch/bm0146/k204221/iow/iow_data_004.tar
21  -rw-r--r--t  k204221  bm0146  2.047869e+10 2020-06-05  17:58   /arch/bm0146/k204221/iow/iow_data_005.tar
22  -rw-r-----t  k204221  bm0146  8.364491e+09 2020-06-05  17:57   /arch/bm0146/k204221/iow/iow_data_006.tar

# check if a file exists
> pyslk.resource_exists("/arch/bm0146/k204221/iow/iow_data2_001.tar")
True
# check another non-existing file
> pyslk.resource_exists("/arch/bm0146/k204221/iow/NOT_EXISTS.tar")
False
# get metadata of a file
> pyslk.get_metadata("/arch/bm0146/k204221/iow/INDEX.txt")
{'netcdf.Title': 'ABC DEF GHI'}
# get size
> pyslk.get_resource_size("/arch/bm0146/k204221/iow/INDEX.txt")
1268945
# get checksums
> pyslk.get_checksum("/arch/bm0146/k204221/iow/INDEX.txt")
{'adler32': '412dec3a',
 'sha512': '83644ffc384c70aaf60d29f3303d771e219f3b3f8abdb3a590ac501faf7abbeb371ee4b6b949a1cdc3fa7c44438cd6643f877e8c1ab27d8fe5cc26eb06896d99'}
# is the file stored in the cache? yet!
> pyslk.is_cached("/arch/bm0146/k204221/iow/INDEX.txt")
True
# retrieve file
> pyslk.retrieve("/arch/bm0146/k204221/iow/INDEX.txt", '.', preserve_path=False)
''
> os.path.exists('INDEX.txt')
True
```

### Search

We want to search for files, which are stored in `/arch/bm0146/k204221/iow`, are larger than 1 kb and smaller
than approximately 2 MB.

```python
# load pyslk
import pyslk.core.gen_queries
import pyslk.base.searching
> import pyslk
# generate search query
> search_query = pyslk.gen_search_query(["path=/arch/bm0146/k204221/iow", "resources.size>1024", "resources.size<2000000"])
> search_query
'{"$and":[{"resources.size":{"$gt":1024}},{"resources.size":{"$lt":2000000}},{"path":{"$gte":"/arch/bm0146/k204221/iow","$max_iterations":1}}]}'
# run search
> search_id = pyslk.search(search_query)
> search_id
677761
# list search results
> pyslk.list(search_id)
   permissions    owner   group   filesize       date   time                            filename
0  -rwxr-xr-x-  k204221  bm0146  1268945.0 2020-06-10  08:25  /arch/bm0146/k204221/iow/INDEX.txt
```

or just

```python
> import pyslk
> pyslk.list(pyslk.search(pyslk.core.gen_queries.gen_search_query(["path=/arch/bm0146/k204221/iow", "resources.size>1024", "resources.size<2000000"])))
   permissions    owner   group   filesize       date   time                            filename
0  -rwxr-xr-x-  k204221  bm0146  1268945.0 2020-06-10  08:25  /arch/bm0146/k204221/iow/INDEX.txt
```

### Split file list per tape for retrieval

split large retrieval request

This should be done in two terminals!

Terminal 1: recall

```python
> import pyslk
> output = pyslk.group_files_by_tape("/arch/bm0146/k204221/iow", recursive=True)
> output
[{'id': -1, 'location': 'cache', 'description': 'files currently stored in the HSM cache', 'barcode': '', 'status': '', 'file_count': 2, 'files': ['/arch/bm0146/k204221/iow/iow_data4_001.tar', '/arch/bm0146/k204221/iow/INDEX.txt'], 'file_ids': [49058705506, 49058705497], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"smart_pool":"slpstor"}]}'}, {'id': 93505, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'M10211M8', 'status': 'AVAILABLE', 'file_count': 1, 'files': ['/arch/bm0146/k204221/iow/iow_data3_001.tar'], 'file_ids': [49058705504], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"M10211M8"}]}'}, {'id': 75696, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25543L6', 'status': 'AVAILABLE', 'file_count': 2, 'files': ['/arch/bm0146/k204221/iow/iow_data_006.tar', '/arch/bm0146/k204221/iow/iow_data2_001.tar'], 'file_ids': [49058705519, 49058705498], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25543L6"}]}'}, {'id': 75719, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25566L6', 'status': 'AVAILABLE', 'file_count': 2, 'files': ['/arch/bm0146/k204221/iow/iow_data5_006.tar', '/arch/bm0146/k204221/iow/iow_data5_002.tar'], 'file_ids': [49058705513, 49058705509], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25566L6"}]}'}, {'id': 75718, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25565L6', 'status': 'AVAILABLE', 'file_count': 1, 'files': ['/arch/bm0146/k204221/iow/iow_data5_004.tar'], 'file_ids': [49058705511], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25565L6"}]}'}, {'id': 75691, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25538L6', 'status': 'AVAILABLE', 'file_count': 5, 'files': ['/arch/bm0146/k204221/iow/iow_data_004.tar', '/arch/bm0146/k204221/iow/iow_data3_002.tar', '/arch/bm0146/k204221/iow/iow_data2_006.tar', '/arch/bm0146/k204221/iow/iow_data2_004.tar', '/arch/bm0146/k204221/iow/iow_data2_003.tar'], 'file_ids': [49058705517, 49058705505, 49058705503, 49058705501, 49058705500], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25538L6"}]}'}, {'id': 75723, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25570L6', 'status': 'AVAILABLE', 'file_count': 1, 'files': ['/arch/bm0146/k204221/iow/iow_data5_003.tar'], 'file_ids': [49058705510], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25570L6"}]}'}, {'id': 75690, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25537L6', 'status': 'AVAILABLE', 'file_count': 1, 'files': ['/arch/bm0146/k204221/iow/iow_data_002.tar'], 'file_ids': [49058705515], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25537L6"}]}'}, {'id': 75722, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25569L6', 'status': 'AVAILABLE', 'file_count': 2, 'files': ['/arch/bm0146/k204221/iow/iow_data5_005.tar', '/arch/bm0146/k204221/iow/iow_data5_001.tar'], 'file_ids': [49058705512, 49058705508], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25569L6"}]}'}, {'id': 75693, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25540L6', 'status': 'AVAILABLE', 'file_count': 1, 'files': ['/arch/bm0146/k204221/iow/iow_data_005.tar'], 'file_ids': [49058705518], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25540L6"}]}'}, {'id': 75692, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25539L6', 'status': 'AVAILABLE', 'file_count': 2, 'files': ['/arch/bm0146/k204221/iow/iow_data_003.tar', '/arch/bm0146/k204221/iow/iow_data4_002.tar'], 'file_ids': [49058705516, 49058705507], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25539L6"}]}'}, {'id': 75695, 'location': 'tape', 'description': 'files stored on the tape with the given ID and barcode/label', 'barcode': 'C25542L6', 'status': 'AVAILABLE', 'file_count': 3, 'files': ['/arch/bm0146/k204221/iow/iow_data_001.tar', '/arch/bm0146/k204221/iow/iow_data2_002.tar', '/arch/bm0146/k204221/iow/iow_data2_005.tar'], 'file_ids': [49058705514, 49058705499, 49058705502], 'search_query': '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},{"tape_barcode":"C25542L6"}]}'}]
> tapeJobMapping: dict = dict()
# iterate files on normal tapes:
> for iFileSet in output:
    if iFileSet["id"] > 0:
        tapeJobMapping[iFileSet["barcode"]] = pyslk.recall_single(iFileSet["file_ids"], resource_ids=True)
    # wait if 4 recalls are running ...
# get split files (files on more than one tape); JSON looks like this:
#  {
#    "id": -1,
#    "location": "tape",
#    "description": "files stored on more than one tape",
#    "barcode": "",
#    "status": "",
#    "file_count": 1,
#    "files": [
#      "/arch/pd1309/forcings/reanalyses/ERA5/year1999/ERA5_1999_03_part2.tar"
#    ],
#    "file_ids": [
#      49083773276
#    ],
#    "search_query": "{\"$and\":[{\"path\":{\"$gte\":\"/arch/pd1309/forcings/reanalyses/ERA5/year1999\",\"$max_depth\":1}},{\"resources.name\":{\"$regex\":\"ERA5_1999_03_part2.tar\"}}]}"
#  }

> for iFileSet in output:
    if iFileSet["id"] == -1 and iFileSet["location"] == "tape":
        for fileId in iFileSet["file_ids"]:
            pyslk.recall_single(fileId, resource_ids=True)
        # wait if 4 recalls are running ...
```

Terminal 2: retrieval

```python
> import pyslk
> pyslk.retrieve_improved("/arch/bm0146/k204221/iow", destination="/work/ab1234/test", recursive=True, preserve_path=True, dry_run=True)
pyslk.retrieve_improved("/arch/bm0146/k204221/iow", destination=".", recursive=True, preserve_path=True, dry_run=True)
{'FAILED': {'FAILED_NOT_CACHED': ['/arch/bm0146/k204221/iow/iow_data_006.tar', ...]}, 'ENVISAGED': {'ENVISAGED': ['/arch/bm0146/k204221/iow/iow_data4_001.tar', '/arch/bm0146/k204221/iow/INDEX.txt']}, 'FILES': {'/arch/bm0146/k204221/iow/iow_data_006.tar': '/work/ab1234/test/./arch/bm0146/k204221/iow/iow_data_006.tar', ..., '/arch/bm0146/k204221/iow/INDEX.txt': '/work/ab1234/test/./arch/bm0146/k204221/iow/INDEX.txt'}}
# the 'ENVISAGED' files will be retrieved
> pyslk.retrieve_improved("/arch/bm0146/k204221/iow", destination="/work/ab1234/test", recursive=True, preserve_path=True)
# ... retrieval running ...
```


### `pyslk` in the DKRZ jupyterhub

To make use of `pyslk` in the jupyterhub, you have to make the `slk` executable
available in the `PATH` environment variable. You can do this by creating your own
`kernel.json` file, e.g.,

```console
module load slk
python -m ipykernel install --name slk --display-name "hsm kernel" --env PATH $PATH --env JAVA_HOME $JAVA_HOME --user
```

You need to restart the kernel if you modified/replaced an existing `kernel.json`. You can find
your `kernel.json`, e.g., in `.local/share/jupyter/kernels/your_kernel` depending
on where you store your kernel files (probably in your `$HOME` directory).

If you want to use a different version of `slk`, you have to update the path to your executable.

See also [here](https://jupyterhub.gitlab-pages.dkrz.de/jupyterhub-docs/posts/2020/nosuchfile.html).

## Contributing

Anyone is welcome to contribute to the code. Please check the HTML documentation for details:

* https://hsm-tools.gitlab-pages.dkrz.de/pyslk/development.html


## Acknowledgements

Martin Bergemann (DKRZ), Dogus Kaan Bilir (DKRZ), Lars Buntemeyer (GERICS), Carsten Ehbrecht (DKRZ), Andrej Fast (DKRZ), Helge Heuer (DLR), Karsten Peters-von Gehlen (DKRZ), Fabian Wachsmann (DKRZ) and Karl-Hermann Wieners (MPI-M) contributed to this package. They are listed in alphabetical order.
