"""Execution output properties helper.

The properties are saved in a `valohai.metadata.jsonl` file in the outputs directory
in JSON lines format.
"""

import json
import logging
from collections import Counter, defaultdict
from itertools import chain
from pathlib import Path
from typing import Any, DefaultDict, Dict, Union

from valohai.paths import get_outputs_path

File = Union[str, Path]  # path to the file (relative to outputs directory)
Properties = Dict[str, Any]  # metadata properties for a file
FilesProperties = DefaultDict[File, Properties]
DatasetVersionURI = str  # dataset version URI (e.g. 'dataset://dataset-1/version')

logger = logging.getLogger()


class OutputProperties:
    """Helper for setting properties for output files."""

    _files_properties: FilesProperties

    def __init__(self) -> None:
        self._files_properties = defaultdict(FilesProperties)
        self.properties_file = Path(get_outputs_path()) / "valohai.metadata.jsonl"

    def __enter__(self) -> "OutputProperties":
        self._initialize_existing_properties()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self._save()
        self._log_created_datasets()

    def add(
        self,
        *,
        file: File,
        properties: Properties,
    ) -> None:
        """
        Add properties to a file.
        If the file already has properties, the new properties will be added to them.

        Args:
            file: The path to the file (relative to the execution outputs root directory).
            properties: The metadata properties for the file.
        """
        self._files_properties[str(file)].update(properties)

    def add_to_dataset(self, *, file: File, dataset_version: DatasetVersionURI) -> None:
        """
        Add a file to a dataset.

        Args:
            file: The path to the file (relative to the execution outputs root directory).
            dataset_version: The dataset version to add the file to.
        """
        dataset_versions = set(
            self._files_properties[str(file)].get("valohai.dataset-versions", [])
        )
        dataset_versions.add(dataset_version)
        self.add(
            file=file,
            properties={"valohai.dataset-versions": list(dataset_versions)},
        )

    @staticmethod
    def dataset_version_uri(dataset: str, version: str) -> DatasetVersionURI:
        """Return the dataset URI for the given dataset and version."""
        return f"dataset://{dataset}/{version}"

    def _initialize_existing_properties(self) -> None:
        try:
            for json_line in self.properties_file.read_bytes().splitlines():
                line = json.loads(json_line)
                if isinstance(line.get("file"), str) and "metadata" in line:
                    self._files_properties[line["file"]] = line["metadata"]
        except FileNotFoundError:
            return

    def _save(self) -> None:
        self.properties_file.write_text(
            "".join(
                format_line(file_path, file_metadata)
                for file_path, file_metadata in self._files_properties.items()
            )
        )

    def _log_created_datasets(self) -> None:
        """Print out a summary of created datasets to the execution log."""
        datasets = [
            file_metadata["valohai.dataset-versions"]
            for file_metadata in self._files_properties.values()
            if file_metadata.get("valohai.dataset-versions")
        ]
        if not datasets:
            return
        dataset_counter = Counter(chain.from_iterable(datasets))
        for dataset, nr_of_files in dataset_counter.items():
            print(f"Created dataset version '{dataset}' with {nr_of_files:,} files")  # noqa: T201


output_properties = OutputProperties


def format_line(file_path: File, file_metadata: Properties) -> str:
    """Format metadata for an output file into a format Valohai understands.

    Args:
        file_path: The path to the file (relative to the execution outputs root directory).
        file_metadata: The metadata for the file.
    """
    return (
        json.dumps(
            {
                "file": file_path,
                "metadata": file_metadata,
            }
        )
        + "\n"
    )
