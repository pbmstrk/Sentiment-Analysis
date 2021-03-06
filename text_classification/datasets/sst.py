import os
from functools import partial
from typing import Callable, Optional, Tuple

from ..utils import download_extract
from ..utils.datasets import get_data_from_file, map_list_to_example, parse_line_tree
from .base import DATASETS, TextDataset


def SSTDataset(
    root: str = ".data",
    name: str = "sst",
    train_subtrees: bool = False,
    fine_grained: bool = False,
    tokenizer: Optional[Callable] = None,
    filter_func: Optional[Callable] = None,
    override: bool = False,
) -> Tuple[TextDataset, TextDataset, TextDataset]:

    r"""
    Load the Stanford Sentiment Treebank (SST) Dataset

    Function to load train, validation and test subsets, tokenize
    and filter examples.

    Source:  `SST <https://nlp.stanford.edu/sentiment/index.html>`_

    Args:
        root: Name of the root directory in which to store data.
        name: Name of the folder within root directory to store data.
        train_subtrees: Include all subtrees in training set.
        fine_grained: Use fine-grained classification (5 classes).
        tokenizer: Tokenizer function to tokenize strings into a list of tokens.
        filter_func: Function used to filter out examples. At the stage of filtering,
            each example is represented by a dataclass with two attributes: text and label
        override: Boolean indicating whether previously downloaded dataset should be overriden.

    Returns:
        Processed train, val and test datasets

    Example::

        # To include subtrees in training set
        >>> train, val, test = SSTDataset(train_subtrees=True)
        # To remove all neutral examples
        >>> train, val, test = SSTDataset(filter_func=lambda x: x.label != 'neutral')
    """

    dir_name = "trees"

    # adapted from https://github.com/pytorch/text/blob/master/torchtext/datasets/sst.py#L34-L36
    prefix = "very " if fine_grained else ""
    label_map = {
        "0": prefix + "negative",
        "1": "negative",
        "2": "neutral",
        "3": "positive",
        "4": prefix + "positive",
    }

    # download and extract dataset
    url = DATASETS["sst"]
    download_extract(url, name, root=root, override=override)

    # define a parser to format each example - use partial to supply additional
    # arguments
    train_parser = partial(parse_line_tree, subtrees=train_subtrees)
    val_test_parser = partial(parse_line_tree, subtrees=False)

    # get data from all files using defined parser
    train = get_data_from_file(
        os.path.join(root, name, dir_name, "train.txt"), train_parser
    )
    val = get_data_from_file(
        os.path.join(root, name, dir_name, "dev.txt"), val_test_parser
    )
    test = get_data_from_file(
        os.path.join(root, name, dir_name, "test.txt"), val_test_parser
    )

    # data: List of lists. Using map function to filter, tokenize and convert to list of Examples
    map_f = partial(
        map_list_to_example,
        tokenizer=tokenizer,
        filter_func=filter_func,
        label_map=label_map,
    )

    return (
        TextDataset([x for x in map(map_f, train) if x]),
        TextDataset([x for x in map(map_f, val) if x]),
        TextDataset([x for x in map(map_f, test) if x]),
    )
