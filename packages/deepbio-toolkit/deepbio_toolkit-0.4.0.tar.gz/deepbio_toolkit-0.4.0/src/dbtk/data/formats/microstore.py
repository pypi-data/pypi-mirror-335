from collections import deque
import deflate
import hashlib
import io
import mmap
import os
import numpy as np
from pathlib import Path
from tqdm import tqdm
from typing import Dict, Iterable, List, Optional, Tuple, Union
from ..._utils import export

CHECKSUM_SIZE = 20
INDEX_SIZE = 3*8
RECORD_SIZE = CHECKSUM_SIZE + INDEX_SIZE

@export
class MicroStore:
    """
    A small key-value store that stores values in a sorted array on disk with fast access via memory-mapping.
    """

    def __init__(
        self,
        path: Union[Path, str],
        value_transform: Optional[Callable, bytes] = None
    ):
        # Create the store
        self.path = Path(path)
        if not self.path.exists():
            self.path.mkdir(parents=False)
        elif self.hashtable_path.exists() != self.data_path.exists():
            raise ValueError("Broken format: keys and values must both exist or not exist.")
        if not self.hashtable_path.exists():
            with open(self.hashtable_path, "wb") as f:
                f.write(b"\x00")
        if not self.data_path.exists():
            with open(self.data_path, "wb") as f:
                f.write(b"\x00")

        # Open the store
        self.length = self.hashtable_path.stat().st_size // RECORD_SIZE
        self._hashtable_file_handle = open(self.hashtable_path, "r+b")
        self._data_file_handle = open(self.data_path, "r+b")
        self._hashtable_mmap = mmap.mmap(self._hashtable_file_handle.fileno(), 0, access=mmap.ACCESS_WRITE)
        self._data_mmap = mmap.mmap(self._data_file_handle.fileno(), 0, access=mmap.ACCESS_READ)


    @property
    def hashtable_path(self) -> Path:
        return self.path / "keys.dat"


    @property
    def data_path(self) -> Path:
        return self.path / "values.dat"


    def close(self):
        """
        Close the MicroStore and release resources.
        """
        self._hashtable_mmap.close()
        self._data_mmap.close()
        self._hashtable_file_handle.close()
        self._data_file_handle.close()


    def _bisect(
        self,
        key_hash: bytes,
        *,
        _left: Optional[int] = None,
        _right: Optional[int] = None
    ) -> int:
        """
        Get the current index of a key.

        Args:
            key (str): The key to lookup.

        Raises:
            KeyError: If the key is not found.

        Returns:
            int: The index of the key.
        """
        left = _left if _left is not None else 0
        right = _right if _right is not None else self.length - 1
        while left <= right:
            mid = (left + right) // 2
            offset = mid * RECORD_SIZE
            record = self._hashtable_mmap[offset:offset + RECORD_SIZE]
            if record[:CHECKSUM_SIZE] == key_hash:
                return mid
            elif record[:CHECKSUM_SIZE] < key_hash:
                left = mid + 1
            else:
                right = mid - 1
        return left

    def _compress(self, data: bytes) -> bytes:
        """
        Compress the given data using the deflate algorithm.

        Args:
            data (bytes): The data to compress.

        Returns:
            bytes: The compressed data.
        """
        return np.uint32(len(data)).tobytes() + deflate.deflate_compress(data)


    def _decompress(self, data: bytes) -> bytes:
        """
        Decompress the given data using the deflate algorithm.

        Args:
            data (bytes): The data to decompress.

        Returns:
            bytes: The decompressed data.
        """
        length = np.frombuffer(data, dtype=np.uint32, count=1)[0]
        return deflate.deflate_decompress(data[4:], length)


    def _hash(self, data: bytes) -> bytes:
        """
        Compute the SHA1 hash of the given data.

        Args:
            data (bytes): The data to hash.

        Returns:
            bytes: The hash of the data.
        """
        return hashlib.sha1(data).digest()


    def key(self, index: int) -> bytes:
        """
        Get the key associated with an index.

        Args:
            index (int): The index to lookup.

        Raises:
            KeyError: If the index is out of bounds.

        Returns:
            bytes: The key associated with the index.
        """
        if index < 0 or index >= self.length:
            raise KeyError(index)
        offset = index*RECORD_SIZE
        record_info = self._hashtable_mmap[offset + CHECKSUM_SIZE:offset + RECORD_SIZE]
        key_start, key_end, _ = np.frombuffer(record_info, count=3, dtype=np.uint64)
        return self._decompress(self._data_mmap[key_start:key_end])


    def get(self, key_or_index: Union[int, bytes]) -> bytes:
        """
        Get the value associated with a key or index.

        Args:
            key_or_index (Union[int, bytes]): The key or index to lookup.

        Raises:
            KeyError: If the key is not found.
            KeyError: If the index is out of bounds.
            TypeError: If the key type is not bytes.

        Returns:
            bytes: The value associated with the key or index.
        """
        if isinstance(key_or_index, bytes):
            key_hash =  self._hash(key_or_index)
            index = self._bisect(key_hash)
            offset = index*RECORD_SIZE
            if self._hashtable_mmap[offset:offset + CHECKSUM_SIZE] != key_hash:
                raise KeyError(key_or_index)
        elif isinstance(key_or_index, int):
            index = key_or_index
            offset = index*RECORD_SIZE
            if index < 0 or index >= self.length:
                raise KeyError(index)
        else:
            raise TypeError(f"Unsupported key type: {type(key_or_index)}")
        _, value_start, value_end = np.frombuffer(self._hashtable_mmap[offset + CHECKSUM_SIZE:offset + RECORD_SIZE], count=3, dtype=np.uint64)
        return self._decompress(self._data_mmap[value_start:value_end])


    def _to_insert(
        self,
        keys_and_values: Iterable[Tuple[bytes, bytes]],
        show_progress: bool = False
    ) -> Dict[bytes, Tuple[int, bytes, bytes]]:
        """
        Filter out duplicates and compute insertion points for the given keys and values.

        Args:
            keys_and_values (Iterable[Tuple[bytes, bytes]]): The keys and values to insert.

        Returns:
            Dict[bytes, Tuple[int, bytes, bytes]]: A dictionary of insertion points.
        """
        left = 0
        to_insert = {}
        keys_and_values = sorted(tqdm(keys_and_values, disc="Sorting...", disable=(not show_progress), leave=False))
        for key, value in tqdm(keys_and_values, desc="Computing insertion points...", disable=(not show_progress), leave=False):
            key_hash = self._hash(key)
            # Check for duplicates in batch
            if key_hash in to_insert:
                continue
            left = self._bisect(key_hash, _left=left)
            offset = left*RECORD_SIZE
            # Check for duplicates on disk
            if self._hashtable_mmap[offset:offset + CHECKSUM_SIZE] == key_hash:
                # Skip this entry as it already exists.
                continue
            to_insert[key_hash] = (left, self._compress(key), self._compress(value))

        # Sort the insertions by hash index
        to_insert = sorted(to_insert.items(), key=lambda x: (x[1][0], x[0]))


    def _insert(
        self,
        to_insert: Dict[bytes, Tuple[int, bytes, bytes]],
        show_progress: bool = False
    ):
        """
        [Unsafe] Insert the given keys and values into the MicroStore.

        Args:
            to_insert (Dict[bytes, Tuple[int, bytes, bytes]]): The keys and values to insert.
            show_progress (bool, optional): Show progress during insertion. Defaults to False.
        """
        # Resize the hashtable file and mmap to fit the new keys
        new_length = self.length + len(to_insert)
        new_size = new_length * RECORD_SIZE
        self._hashtable_file_handle.truncate(new_size)
        self._hashtable_mmap.resize(new_size)
        madvise = self._hashtable_mmap.madvise(0, 0)
        self._hashtable_mmap.madvise(mmap.MADV_SEQUENTIAL)

        # Write the new keys to the hashtable
        q = deque(maxlen=len(to_insert) + 1)
        if self.length == 0:
            self._data_file_handle.seek(0)
        else:
            self._data_file_handle.seek(0, io.SEEK_END)
        data_start = np.uint64(self._data_file_handle.tell())
        for i, (key_hash, (index, key, value)) in enumerate(tqdm(to_insert, desc="Writing...", disable=(not show_progress), leave=False)):
            index += i # account for previous insertions
            offset = index*RECORD_SIZE
            # Compute data record info
            key_end = np.uint64(data_start + len(key))
            value_end = np.uint64(key_end + len(value))
            record_info = key_hash + data_start.tobytes() + key_end.tobytes() + value_end.tobytes()
            data_start = value_end
            # Insert record info into the hashtable
            q.append(self._hashtable_mmap[offset:offset + RECORD_SIZE])
            self._hashtable_mmap[offset:offset + RECORD_SIZE] = record_info
            # Propogate the values down to the next index
            end = RECORD_SIZE*(to_insert[i+1][1][0] + i + 1 if i+1 < len(to_insert) else new_length)
            for j in range(offset + RECORD_SIZE, end, RECORD_SIZE):
                q.append(self._hashtable_mmap[j:j + RECORD_SIZE])
                self._hashtable_mmap[j:j + RECORD_SIZE] = q.popleft()

        # Write the new data to the store and update the memory map
        self._data_file_handle.write(b"".join([key + value for _, (_, key, value) in to_insert]))
        self._data_file_handle.seek(0)
        self._data_mmap.close()
        self._data_mmap = mmap.mmap(self._data_file_handle.fileno(), 0, access=mmap.ACCESS_READ)

        # Update the length
        self.length = new_length
        self._hashtable_mmap.madvise(madvise)


    def write(self, key: bytes, value: bytes):
        """
        Write a key/value pair to the MicroStore.

        Args:
            key (bytes): The key to write.
            value (bytes): The value to write.
        """
        self.batch_write([(key, value)])


    def batch_write(
        keys_and_values: Iterable[Tuple[bytes, bytes]],
        show_progress: bool = False
    ) -> Dict[bytes, Tuple[int, bytes, bytes]]:
        """
        Write multiple key/value pairs to the MicroStore.

        Args:
            keys_and_values (Iterable[Tuple[bytes, bytes]]): The keys and values to write.
            show_progress (bool, optional): Show progress during insertion. Defaults to False.
        """
        to_insert = self._to_insert(keys_and_values, show_progress)
        self._insert(to_insert, show_progress)


    def __getitem__(self, key_or_index: Union[int, bytes]) -> bytes:
        return self.get(key_or_index)


    def __len__(self) -> int:
        return self.length
