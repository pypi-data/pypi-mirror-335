from pathlib import Path
from typing import Union
from .microstore import MicroStore

class IndexStore(MicroStore):
    def _to_insert(self, keys_and_values: Iterable[Tuple[bytes, bytes]]):
        to_insert = super()._to_insert(keys_and_values)
        for _, value in to_insert:
        return to_insert

    def write(self, key: bytes):
        return self.batch_write([(key, b"")])

class SequenceStore:
    class Writer:
        def __init__(self, path: Union[str, Path]):
            self.sequence_store = IndexStore(path / "sequences.dat")
            self._sequence_id_store = None

        @property
        def sequence_id_store(self):
            if self._sequence_id_store is None:
                self._sequence_id_store = IndexStore(self.sequence_store.path / "sequence_ids.dat")
            return self._sequence_id_store

        def write(self, sequences: Iterable[Sequence]):
            self.sequence_store.write(zip(sequences, ))

