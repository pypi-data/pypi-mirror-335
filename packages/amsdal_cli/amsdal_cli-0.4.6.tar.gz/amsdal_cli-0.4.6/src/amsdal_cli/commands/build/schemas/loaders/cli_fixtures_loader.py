import json
import logging
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pandas as pd
from amsdal_utils.schemas.schema import ObjectSchema

from amsdal_cli.commands.build.schemas.loaders.base import FixturesLoaderBase

FIXTURES = 'fixtures'

logger = logging.getLogger(__name__)

FIXTURES_JSON_FILE = 'fixtures.json'
MODEL_JSON_FILE = 'model.json'


class CliFixturesLoader(FixturesLoaderBase):
    """
    Loader for fixtures in CLI.

    This class is responsible for loading fixtures from a given schema directory. It extends the `FixturesLoaderBase`
    to provide methods for iterating over fixture files and directories.
    """

    def __init__(self, schema_dir: Path) -> None:
        self.models_with_fixtures: list[tuple[Path, ObjectSchema]] = []

        if schema_dir.exists():
            for item in schema_dir.iterdir():
                if (
                    item.is_dir()
                    and (item / MODEL_JSON_FILE).exists()
                    and (item / FIXTURES).exists()
                    and (item / FIXTURES).is_dir()
                ):
                    self.models_with_fixtures.append(
                        (
                            item,
                            ObjectSchema.model_validate_json((item / MODEL_JSON_FILE).read_text('utf-8')),
                        ),
                    )

    def iter_fixtures(self) -> Iterator[Path]:
        """
        Iterates over fixture files and yields their paths.

        This method creates a temporary directory and writes fixture data to a JSON file within that directory.
            It collects fixture data from CSV and JSON files in the model directories and writes them to the JSON file.
            The path to the JSON file is then yielded.

        Yields:
            Iterator[Path]: An iterator over the paths to the JSON files containing the fixture data.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            new_fixtures_path = Path(temp_dir, FIXTURES_JSON_FILE)

            with new_fixtures_path.open('w') as new_fixtures_file:
                fixtures = []

                for model_dir, model_config in self.models_with_fixtures:
                    for entity_item in (model_dir / FIXTURES).iterdir():
                        _data: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None

                        if entity_item.name.endswith('.csv'):
                            _data = pd.read_csv(entity_item).fillna('').to_dict(orient='records')  # type: ignore[assignment]
                        elif entity_item.name.endswith('.json'):
                            with entity_item.open() as f:
                                _data = json.load(f)

                        if _data:
                            if isinstance(_data, list):
                                class_name = model_config.title

                                for fixture_element in _data:
                                    external_id = fixture_element.pop('_external_id', None)

                                    if not external_id and 'external_id' in fixture_element:
                                        external_id = fixture_element.pop('external_id')

                                    order = fixture_element.pop('_order', 0)

                                    fixtures.append(
                                        {
                                            'class_name': class_name,
                                            'external_id': external_id,
                                            'order': order,
                                            'data': fixture_element,
                                        },
                                    )

                            else:
                                for class_name, fixture_elements in _data.items():
                                    for fixture_element in fixture_elements:
                                        external_id = fixture_element.pop('_external_id', None)

                                        if not external_id and 'external_id' in fixture_element:
                                            external_id = fixture_element.pop('external_id')

                                        order = fixture_element.pop('_order', 0)
                                        fixtures.append(
                                            {
                                                'class_name': class_name,
                                                'external_id': external_id,
                                                'order': order,
                                                'data': fixture_element,
                                            },
                                        )

                if not fixtures:
                    return

                json.dump(fixtures, new_fixtures_file, indent=4)

            yield new_fixtures_path

    def iter_fixture_files(self) -> Iterator[Path]:
        """
        Iterates over fixture files and yields their paths.

        This method creates a temporary directory and copies fixture files from the model directories to this temporary
        directory. It then yields the path to the temporary directory containing the copied fixture files.

        Yields:
            Iterator[Path]: An iterator over the paths to the temporary directories containing the copied fixture files.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = Path(temp_dir)

            for model_dir, model_config in self.models_with_fixtures:
                files_dir = model_dir / 'fixtures' / 'files'

                if not (files_dir.exists() and files_dir.is_dir()):
                    continue

                for _file in files_dir.iterdir():
                    if _file.is_dir():
                        continue

                    new_file_path = temp_file_path / model_config.title
                    new_file_path.mkdir(parents=True, exist_ok=True)

                    shutil.copy(_file, new_file_path)

            if len(list(temp_file_path.iterdir())) == 0:
                return

            yield temp_file_path

    def __str__(self) -> str:
        return f'{self.__class__.__name__}'


class CliMultiFixturesLoader(CliFixturesLoader):
    """
    Loads multiple fixtures from specified schema directories.

    Attributes:
        models_with_fixtures (list[tuple[Path, ObjectSchema]]): List of tuples containing the path and object schema
            of models with fixtures.
    """

    def __init__(self, schema_dirs: list[Path]) -> None:
        self.models_with_fixtures: list[tuple[Path, ObjectSchema]] = []

        for schema_dir in schema_dirs:
            if not schema_dir.exists():
                continue

            for item in schema_dir.iterdir():
                if (
                    item.is_dir()
                    and (item / MODEL_JSON_FILE).exists()
                    and (item / FIXTURES).exists()
                    and (item / FIXTURES).is_dir()
                ):
                    self.models_with_fixtures.append(
                        (
                            item,
                            ObjectSchema.model_validate_json((item / MODEL_JSON_FILE).read_text('utf-8')),
                        ),
                    )
