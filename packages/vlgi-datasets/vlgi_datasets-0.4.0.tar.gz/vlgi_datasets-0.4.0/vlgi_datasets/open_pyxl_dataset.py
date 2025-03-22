from kedro.io import AbstractVersionedDataSet, Version
from openpyxl import Workbook, load_workbook
from pathlib import Path
from typing import Dict, Any

class OpenPyxlExcelDataSet(AbstractVersionedDataSet):
    """
    Custom dataset for handling Excel files with openpyxl library.
    See
    --
    https://theforce.hashnode.dev/exporting-workbooks-from-kedro-with-openpyxl
    """

    def __init__(self, filepath: str, version: Version = None):
        """Initialize the dataset.
        
        Args:
            filepath: The location of the Excel file.
        """
        super().__init__(filepath=Path(filepath), version=version)

    def _load(self) -> Workbook:
        """Load the Excel file.

        Returns:
            An openpyxl Workbook object.
        """
        return load_workbook(filename=self._filepath)

    def _save(self, data: Workbook) -> None:
        """Save the Excel workbook to the file.
        
        Args:
            data: An openpyxl Workbook object to be saved.
        """
        data.save(filename=self._filepath)

    def _describe(self) -> Dict[str, Any]:
        """Describe the dataset.

        Returns:
            A dictionary that includes the file path to the Excel file.
        """
        return {"filepath": str(self._filepath),
                "version": self._version,
                }
