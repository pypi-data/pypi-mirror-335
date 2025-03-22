import re
from copy import deepcopy
from typing import Any, Dict, Union

import pandas as pd
from kedro.extras.datasets.pandas import ExcelDataSet
from kedro.io.core import PROTOCOL_DELIMITER, DataSetError, Version
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File


class SharePointExcelDataSet(ExcelDataSet):
    def __init__(
        self,
        filepath: str,
        engine: str = "openpyxl",
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
        version: Version = None,
        credentials: Dict[str, Any] = None,
        fs_args: Dict[str, Any] = None,
    ) -> None:

        if not (
            credentials
            and "username" in credentials
            and credentials["username"]
            and "password" in credentials
            and credentials["password"]
        ):
            raise DataSetError(
                "'username' and 'password' argument cannot be empty. Please "
                "provide a Sharepoint credentials."
            )

        _credentials = deepcopy(credentials) or {}
        self._user_credentials = UserCredential(
            _credentials["username"], _credentials["password"]
        )

        super().__init__(
            filepath, engine, load_args, save_args, version, credentials, fs_args
        )

    def _load(self) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        load_path = str(self._get_load_path())
        if self._protocol == "file":
            # file:// protocol seems to misbehave on Windows
            # (<urlopen error file not on local host>),
            # so we don't join that back to the filepath;
            # storage_options also don't work with local paths
            return pd.read_excel(load_path, **self._load_args)

        load_path = f"{self._protocol}{PROTOCOL_DELIMITER}{load_path}"
        base_url = re.sub("(?<=com).*", "", load_path)

        relative_url = load_path.replace(base_url, "")
        file = (
            File.from_url(load_path)
            .with_credentials(self._user_credentials)
            .execute_query()
        )
        response = file.open_binary(file.context, relative_url)

        return pd.read_excel(
            response.content,
            **self._load_args
            # response.content, storage_options=self._storage_options, **self._load_args
        )
