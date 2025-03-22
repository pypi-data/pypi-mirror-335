import json
import logging
from collections.abc import Iterator
from pathlib import Path

from amsdal.schemas.mixins.check_dependencies_mixin import CheckDependenciesMixin
from amsdal.schemas.mixins.verify_schemas_mixin import VerifySchemasMixin
from amsdal_utils.errors import AmsdalError
from amsdal_utils.models.enums import ModuleType
from amsdal_utils.schemas.schema import ObjectSchema
from pydantic import ValidationError

from amsdal_cli.commands.build.schemas.data_models.schemas_directory import SchemasDirectory
from amsdal_cli.commands.build.schemas.extenders.custom_code_extender import CustomCodeExtender
from amsdal_cli.commands.build.schemas.extenders.options_extender import OptionsExtender
from amsdal_cli.commands.build.schemas.loaders.cli_custom_code_loader import CliCustomCodeLoader
from amsdal_cli.commands.build.schemas.loaders.cli_loader import CliConfigLoader
from amsdal_cli.commands.build.schemas.loaders.cli_options_loader import CliOptionsLoader
from amsdal_cli.commands.build.schemas.mixins.enrich_schemas_mixin import EnrichSchemasMixin

logger = logging.getLogger(__name__)


class BuildSchemasManager(EnrichSchemasMixin, VerifySchemasMixin, CheckDependenciesMixin):
    """
    Manages the building and verification of schemas.

    This class is responsible for loading, enriching, verifying, and checking dependencies of various schemas.
    It handles type, core, contrib, and user schemas, ensuring they are properly loaded and validated.
    """

    _type_schemas: list[ObjectSchema]
    _core_schemas: list[ObjectSchema]
    _contrib_schemas: list[ObjectSchema]
    _user_schemas: list[ObjectSchema]

    def __init__(self, schemas_directories: list[SchemasDirectory]):
        self._schemas_directories = schemas_directories
        super().__init__()

    @property
    def type_schemas(self) -> list[ObjectSchema]:
        """
        Retrieves the list of type schemas.

        This property method loads the type schemas if they are not already loaded and returns them.

        Returns:
            list[ObjectSchema]: A list of type schemas.
        """
        if not hasattr(self, '_type_schemas'):
            self._load_schemas()

        return self._type_schemas

    @property
    def core_schemas(self) -> list[ObjectSchema]:
        """
        Retrieves the list of core schemas.

        This property method loads the core schemas if they are not already loaded and returns them.

        Returns:
            list[ObjectSchema]: A list of core schemas.
        """
        if not hasattr(self, '_core_schemas'):
            self._load_schemas()

        return self._core_schemas

    @property
    def contrib_schemas(self) -> list[ObjectSchema]:
        """
        Retrieves the list of contrib schemas.

        This property method loads the contrib schemas if they are not already loaded and returns them.

        Returns:
            list[ObjectSchema]: A list of contrib schemas.
        """
        if not hasattr(self, '_contrib_schemas'):
            self._load_schemas()

        return self._contrib_schemas

    @property
    def user_schemas(self) -> list[ObjectSchema]:
        """
        Retrieves the list of user schemas.

        This property method loads the user schemas if they are not already loaded and returns them.

        Returns:
            list[ObjectSchema]: A list of user schemas.
        """
        if not hasattr(self, '_user_schemas'):
            self._load_schemas()

        return self._user_schemas

    def verify(self) -> None:
        """
        Loads and verifies all schemas.

        This method ensures that all schemas (type, core, contrib, and user schemas) are loaded and verified.

        Returns:
            None
        """
        self._load_schemas()

    def _load_schemas(self) -> None:
        _type_configs = []
        _core_configs = []
        _contrib_configs = []
        _user_configs = []

        for schemas_directory in self._schemas_directories:
            try:
                for schema in self.load_schemas_from_path(schemas_directory.path):
                    if schemas_directory.module_type == ModuleType.TYPE:
                        _type_configs.append(schema)
                    elif schemas_directory.module_type == ModuleType.CORE:
                        _core_configs.append(schema)
                    elif schemas_directory.module_type == ModuleType.CONTRIB:
                        _contrib_configs.append(schema)
                    elif schemas_directory.module_type == ModuleType.USER:
                        _user_configs.append(schema)
            except ValidationError as e:
                msg = f'Error loading schemas from {schemas_directory.path}: {e}'

                raise AmsdalError(msg) from e

        (
            _enriched_type_configs,
            _enriched_core_configs,
            _enriched_contrib_configs,
            _enriched_user_configs,
        ) = self.enrich_configs(_type_configs, _core_configs, _contrib_configs, _user_configs)

        self._type_schemas = _enriched_type_configs
        self._core_schemas = _enriched_core_configs
        self._contrib_schemas = _enriched_contrib_configs
        self._user_schemas = _enriched_user_configs

        self.verify_schemas(
            self._type_schemas,
            self._core_schemas,
            self._contrib_schemas,
            self._user_schemas,
        )
        self.check_dependencies(
            self._type_schemas,
            self._core_schemas,
            self._contrib_schemas,
            self._user_schemas,
        )

    @staticmethod
    def load_schemas_from_path(schemas_path: Path) -> Iterator[ObjectSchema]:
        """
        Loads schemas from the specified path.

        This method reads schemas from the given path and returns an iterator of `ObjectSchema` objects. It uses various
        loaders and extenders to process the schemas.

        Args:
            schemas_path (Path): The path from which to load the schemas.

        Returns:
            Iterator[ObjectSchema]: An iterator of `ObjectSchema` objects.
        """
        schema_reader = CliConfigLoader(schemas_path)
        options_reader = CliOptionsLoader(schemas_path.parent)
        options_extender = OptionsExtender(options_reader)
        custom_code_reader = CliCustomCodeLoader(schemas_path)
        custom_code_extender = CustomCodeExtender(custom_code_reader)

        for object_schema in schema_reader.iter_configs():
            options_extender.extend(object_schema)
            custom_code_extender.extend(object_schema)

            yield object_schema

        options_extender.post_extend()
        custom_code_extender.post_extend()

    def dump_schemas(self, target_dir: Path) -> None:
        """
        Dumps all schemas to the specified directory.

        This method creates the target directory if it does not exist and writes the type, core, contrib,
            and user schemas to separate JSON files within the directory.

        Args:
            target_dir (Path): The directory where the schemas will be dumped.

        Returns:
            None
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        self._dump_schemas(target_dir / 'type_schemas.json', self.type_schemas)
        self._dump_schemas(target_dir / 'core_schemas.json', self.core_schemas)
        self._dump_schemas(target_dir / 'contrib_schemas.json', self.contrib_schemas)
        self._dump_schemas(target_dir / 'user_schemas.json', self.user_schemas)

    @staticmethod
    def _dump_schemas(target_file: Path, schemas: list[ObjectSchema]) -> None:
        _schemas = [schema.model_dump() for schema in schemas]
        new_schema_titles = [schema.title for schema in schemas]

        if target_file.exists():
            # Leave out schemas that are already in the file.
            # Should be deleted explicitly via API `DELETE /api/classes/{class_name}/`.
            for _schema in json.loads(target_file.read_text()):
                if _schema['title'] not in new_schema_titles:
                    _schemas.append(_schema)

        target_file.write_text(json.dumps(_schemas))

    @classmethod
    def add_user_schema(cls, target_dir: Path, object_schema: ObjectSchema) -> None:
        """
        Adds a user schema to the specified directory.

        This method adds the given `ObjectSchema` to the `user_schemas.json` file in the target directory. If the file
        already exists, it updates the existing schemas by removing any schema with the same title as the new schema
        before adding the new schema.

        Args:
            target_dir (Path): The directory where the user schema will be added.
            object_schema (ObjectSchema): The `ObjectSchema` object to add.

        Returns:
            None
        """
        target_file = target_dir / 'user_schemas.json'

        if target_file.exists():
            data = [_item for _item in json.loads(target_file.read_text()) if _item['title'] != object_schema.title]
        else:
            data = []

        data.append(object_schema.model_dump())
        target_file.write_text(json.dumps(data))


class SchemaManagerHandler:
    """
    Handles schema management operations.

    This class is responsible for loading, invalidating, and providing access to various schemas (type, core, contrib,
        and user schemas) from a specified directory.
    """

    _type_schemas: list[ObjectSchema]
    _core_schemas: list[ObjectSchema]
    _contrib_schemas: list[ObjectSchema]
    _user_schemas: list[ObjectSchema]

    def __init__(self, schemas_directory: Path) -> None:
        self._schemas_directory = schemas_directory

    def invalidate_user_schemas(self) -> None:
        """
        Invalidates the cached user schemas.

        This method removes the cached user schemas, forcing them to be reloaded the next time they are accessed.

        Returns:
            None
        """
        if hasattr(self, '_user_schemas'):
            delattr(self, '_user_schemas')

    @property
    def type_schemas(self) -> list[ObjectSchema]:
        """
        Retrieves the list of type schemas.

        This property method loads the type schemas if they are not already loaded and returns them.

        Returns:
            list[ObjectSchema]: A list of type schemas.
        """
        if not hasattr(self, '_type_schemas'):
            self._load_schemas()

        return self._type_schemas

    @property
    def core_schemas(self) -> list[ObjectSchema]:
        """
        Retrieves the list of core schemas.

        This property method loads the core schemas if they are not already loaded and returns them.

        Returns:
            list[ObjectSchema]: A list of core schemas.
        """
        if not hasattr(self, '_core_schemas'):
            self._load_schemas()

        return self._core_schemas

    @property
    def contrib_schemas(self) -> list[ObjectSchema]:
        """
        Retrieves the list of contrib schemas.

        This property method loads the contrib schemas if they are not already loaded and returns them.

        Returns:
            list[ObjectSchema]: A list of contrib schemas.
        """
        if not hasattr(self, '_contrib_schemas'):
            self._load_schemas()

        return self._contrib_schemas

    @property
    def user_schemas(self) -> list[ObjectSchema]:
        """
        Retrieves the list of user schemas.

        This property method loads the user schemas if they are not already loaded and returns them.

        Returns:
            list[ObjectSchema]: A list of user schemas.
        """
        if not hasattr(self, '_user_schemas'):
            self._load_schemas()

        return self._user_schemas

    @property
    def all_schemas(self) -> list[ObjectSchema]:
        """
        Retrieves the list of all schemas.

        This property method combines and returns the type, core, contrib, and user schemas.

        Returns:
            list[ObjectSchema]: A list of all schemas, including type, core, contrib, and user schemas.
        """
        return self.type_schemas + self.core_schemas + self.contrib_schemas + self.user_schemas

    def _load_schemas(self) -> None:
        self._type_schemas = self._load_schema(self._schemas_directory / 'type_schemas.json')
        self._core_schemas = self._load_schema(self._schemas_directory / 'core_schemas.json')
        self._contrib_schemas = self._load_schema(self._schemas_directory / 'contrib_schemas.json')
        self._user_schemas = self._load_schema(self._schemas_directory / 'user_schemas.json')

    def _load_schema(self, schema_file: Path) -> list[ObjectSchema]:
        with schema_file.open() as f:
            schemas = json.load(f)

        return [ObjectSchema.model_validate(schema) for schema in schemas]
