import os
import ntpath
from pathlib import Path
from typing import Union
from urllib.request import urlretrieve

import pandas as pd

from anndata import read_h5ad, read_loom

url_adata = "https://drive.google.com/uc?export=download&id=1uH5HJ7EqjnF94oovxxCYuB4-Oc6gKBgt"
url_hcmv_annot = "https://drive.google.com/uc?export=download&id=1E_gpsRRuTrrIX8qX4biPejzjiKbD5hKd"


def download_data(url, file_path=None, dir="./datasets"):
    file_path = ntpath.basename(url) if file_path is None else file_path
    file_path = os.path.join(dir, file_path)

    if not os.path.exists(file_path):
        if not os.path.exists("./datasets/"):
            os.mkdir("datasets")

        # download the datasets
        urlretrieve(url, file_path)

    return file_path


def get_adata(url, filename=None):
    """Download example datasets to local folder.

    Parameters
    ----------
        url:
        filename

    Returns
    -------
        adata: :class:`~anndata.AnnData`
            an Annodata object.
    """

    file_path = download_data(url, filename)
    if Path(file_path).suffixes[-1][1:] == "loom":
        adata = read_loom(filename=file_path)
    elif Path(file_path).suffixes[-1][1:] == "h5ad":
        adata = read_h5ad(filename=file_path)

    adata.var_names_make_unique()

    return adata


def hcmv_moDC(
    filename=None,
):
    """ HCMV infected moDCs. 
    """
    adata = get_adata(url_adata, filename)
    return adata

def hcmv_annot(file_path: Union[str, Path] = "datasets/hcmv/hcmv_annot.gtf"):
    annot = pd.read_csv(url_hcmv_annot, sep="\t", header=None)
    annot.to_csv(file_path)
    return annot