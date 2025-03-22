from pathlib import PurePosixPath
from typing import Any, Dict
from copy import deepcopy
import fsspec

from kedro.io import AbstractVersionedDataset, Version
from kedro.io.core import get_filepath_str, get_protocol_and_path


class PDFDataset(AbstractVersionedDataset[Any, Any]):
    """``PDFDataset`` loads / save image data from a given filepath as `numpy` array using Pillow.

    Example:
    ::

        >>> PDFDataset(filepath='/img/file/path.pdf')
    """

    DEFAULT_SAVE_ARGS = {}

    def __init__(self, filepath: str, save_args: Dict[str, Any] = None, version: Version = None, credentials: Dict[str, Any] = None, fs_args: Dict[str, Any] = None):
        """Creates a new instance of PDFDataset to load / save image data for given filepath.

        Args:
            filepath: The location of the image file to load / save data.
        """
        _fs_args = deepcopy(fs_args) or {}
        _fs_open_args_load = _fs_args.pop("open_args_load", {})
        _fs_open_args_save = _fs_args.pop("open_args_save", {})
        _credentials = deepcopy(credentials) or {}

        protocol, path = get_protocol_and_path(filepath, version)

        self._protocol = protocol
        if protocol == "file":
            _fs_args.setdefault("auto_mkdir", True)
        self._fs = fsspec.filesystem(self._protocol, **_credentials, **_fs_args)

        super().__init__(
            filepath=PurePosixPath(path),
            version=version,
            exists_function=self._fs.exists,
            glob_function=self._fs.glob,
        )

        self._save_args = deepcopy(self.DEFAULT_SAVE_ARGS)
        if save_args is not None:
            self._save_args.update(save_args)

        _fs_open_args_save.setdefault("mode", "wb")
        self._fs_open_args_load = _fs_open_args_load
        self._fs_open_args_save = _fs_open_args_save

    def _load(self) -> Any:
        """Loads data from the image file.

        Returns:
            Data from the image file as a numpy array
        """
        load_path = get_filepath_str(self._get_load_path(), self._protocol)
        with self._fs.open(load_path, **self._fs_open_args_load) as f:
            pdf = f.read()
            return pdf

    def _save(self, data: Any) -> None:
        """Saves image data to the specified filepath."""
        save_path = get_filepath_str(self._get_save_path(), self._protocol)
        with self._fs.open(save_path, **self._fs_open_args_save) as f:
            f.write(data)

    def _describe(self) -> Dict[str, Any]:
        """Returns a dict that describes the attributes of the dataset."""
        return dict(filepath=self._get_load_path(), protocol=self._protocol)