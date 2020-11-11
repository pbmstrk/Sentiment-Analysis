from abc import abstractmethod

import torch
from torch.nn.utils.rnn import pad_sequence


class BaseEncoder:
    @abstractmethod
    def __call__(self):
        raise NotImplementedError


class CNNEncoder(BaseEncoder):
    def __init__(self, vocab, target_encoding):
        self.vocab = vocab
        self.target_encoding = target_encoding

    def __call__(self, batch):

        batch = [self._encode(item) for item in batch]

        data = [item[0] for item in batch]
        targets = [item[1] for item in batch]

        # pad the sequences
        x = pad_sequence(data, batch_first=True)

        return x.long(), torch.Tensor(targets).long()

    def _encode(self, example):

        text = torch.tensor([self.vocab[word] for word in example[0]])
        label = torch.tensor(self.target_encoding[example[1]])

        return text, label


class LSTMEncoder(BaseEncoder):
    def __init__(self, vocab, target_encoding):
        self.vocab = vocab
        self.target_encoding = target_encoding

    def __call__(self, batch):

        batch = [self._encode(item) for item in batch]

        data = [item[0] for item in batch]
        targets = [item[1] for item in batch]

        seqlengths = [len(el) for el in data]

        x = pad_sequence(data, batch_first=True)

        return x.long(), torch.Tensor(targets).long(), seqlengths

    def _encode(self, example):

        text = torch.tensor([self.vocab[word] for word in example[0]])
        label = torch.tensor(self.target_encoding[example[1]])

        return text, label


class TransformerEncoder(BaseEncoder):
    def __init__(self, vocab, target_encoding):
        self.vocab = vocab
        self.target_encoding = target_encoding

        assert hasattr(vocab, "cls_token") and hasattr(vocab, "sep_token")

    def __call__(self, batch):

        batch = [self._encode(item) for item in batch]

        data = [item[0] for item in batch]
        targets = [item[1] for item in batch]

        x = pad_sequence(data, batch_first=True)

        return x.long(), torch.Tensor(targets).long()

    def _encode(self, example):

        text = torch.tensor(
            [self.vocab.cls_token]
            + [self.vocab[word] for word in example[0]]
            + [self.vocab.sep_token]
        )
        label = torch.tensor(self.target_encoding[example[1]])

        return text, label
