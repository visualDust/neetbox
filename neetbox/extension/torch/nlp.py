import array
import os
import sys
import zipfile

import torch
from tqdm import tqdm

from neetbox.logging import logger
from neetbox.utils import download

__all__ = ["load_word_vectors"]


def load_word_vectors(root, wv_type, dim):
    """
    Load word vectors from a path, trying .pt, .txt, and .zip extensions.
    Args:
        root: the root path of word vectors.
        wv_type: the type of word vectors, current support [glove.42B, glove.840B, glove.twitter.27B, glove.6B].
        dim: the dimension of word vectors.

    Returns:
        tuple: the tuple of (word vector dict, word vector array, word vector size)
    """
    URL = {
        "glove.42B": "http://nlp.stanford.edu/data/glove.42B.300d.zip",
        "glove.840B": "http://nlp.stanford.edu/data/glove.840B.300d.zip",
        "glove.twitter.27B": "http://nlp.stanford.edu/data/glove.twitter.27B.zip",
        "glove.6B": "http://nlp.stanford.edu/data/glove.6B.zip",
    }
    AVAILABLE = {
        "glove.42B": [300],
        "glove.840B": [300],
        "glove.twitter.27B": [25, 50, 100, 200],
        "glove.6B": [50, 100, 200, 300],
    }

    if wv_type not in AVAILABLE.keys():
        raise ValueError(
            f"no word vector type available, only available for {list(AVAILABLE.keys())}."
        )

    if isinstance(dim, int):
        if dim not in AVAILABLE[wv_type]:
            raise ValueError(f"invalid word vector dimension, only support {AVAILABLE[wv_type]} d.")
        dim = str(dim) + "d"
    fname = os.path.join(root, wv_type + "." + dim)

    if os.path.isfile(fname + ".pt"):
        fname_pt = fname + ".pt"
        logger.log(f"loading word vectors from {fname_pt}.")
        try:
            return torch.load(fname_pt, map_location=torch.device("cpu"))
        except Exception as e:
            logger.err("fail to load the model from {fname_pt}{e}.")
            sys.exit(-1)
    else:
        logger.log(f"File not found: {fname}.pt")
    if not os.path.isfile(fname + ".txt"):
        logger.log(f"File not found: {fname}.txt")
    if os.path.isfile(fname + ".txt"):
        fname_txt = fname + ".txt"
        cm = open(fname_txt, "rb")
        cm = [line for line in cm]
    elif os.path.basename(wv_type) in URL:
        url = URL[wv_type]
        logger.log(f"downloading word vectors from {url}.")
        filename = os.path.basename(fname)
        if not os.path.exists(root):
            os.makedirs(root)
        fname = download(url, fname)
        with zipfile.ZipFile(fname, "r") as zf:
            logger.log(f"extracting word vectors into {root}.")
            zf.extractall(root)
        if not os.path.isfile(fname + ".txt"):
            raise RuntimeError("no word vectors of requested dimension found.")
        return load_word_vectors(root, wv_type, dim)
    else:
        raise RuntimeError("unable to load word vectors.")

    wv_tokens, wv_arr, wv_size = [], array.array("d"), None
    if cm is not None:
        for line in tqdm(range(len(cm)), desc="loading word vectors from {}".format(fname_txt)):
            entries = cm[line].strip().split(b" ")
            word, entries = entries[0], entries[1:]
            if wv_size is None:
                wv_size = len(entries)
            try:
                word = word.decode("utf-8")
            except:
                logger.log(f"non-UTF8 token {repr(word)} was ignored.")
                continue
            wv_arr.extend(float(x) for x in entries)
            wv_tokens.append(word)

    wv_dict = {word: i for i, word in enumerate(wv_tokens)}
    wv_arr = torch.Tensor(wv_arr).view(-1, wv_size)
    ret = (wv_dict, wv_arr, wv_size)
    torch.save(ret, fname + ".pt")
    return ret
