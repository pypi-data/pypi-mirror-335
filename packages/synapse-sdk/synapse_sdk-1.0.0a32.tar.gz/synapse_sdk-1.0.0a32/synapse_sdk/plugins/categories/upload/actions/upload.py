from enum import Enum
from typing import Annotated, Dict, List

from pydantic import AfterValidator, BaseModel, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.clients.utils import get_batched_list
from synapse_sdk.i18n import gettext as _
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.plugins.models import Run
from synapse_sdk.shared.enums import Context
from synapse_sdk.utils.pydantic.validators import non_blank
from synapse_sdk.utils.storage import get_pathlib


class UploadRun(Run):
    pass


class UploadParams(BaseModel):
    """Upload action parameters.

    Args:
        name (str): The name of the action.
        description (str | None): The description of the action.
        checkpoint (int | None): The checkpoint of the action.
        path (str): The path of the action.
        storage (int): The storage of the action.
        collection (int): The collection of the action.
        project (int | None): The project of the action.
        is_generate_tasks (bool): The flag to generate tasks.
        is_generate_ground_truths (bool): The flag to generate ground truths
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: str | None
    path: str
    storage: int
    collection: int
    project: int | None
    is_generate_tasks: bool = False
    is_generate_ground_truths: bool = False

    @field_validator('storage', mode='before')
    @classmethod
    def check_storage_exists(cls, value: str, info) -> str:
        """Validate synapse-backend storage exists.

        TODO: Need to define validation method naming convention.
        TODO: Need to make validation method reusable.
        """
        action = info.context['action']
        client = action.client
        try:
            client.get_storage(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Error occurred while checking storage exists.'))
        return value

    @field_validator('collection', mode='before')
    @classmethod
    def check_collection_exists(cls, value: str, info) -> str:
        """Validate synapse-backend collection exists."""
        action = info.context['action']
        client = action.client
        try:
            client.get_dataset(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Error occurred while checking collection exists.'))
        return value

    @field_validator('project', mode='before')
    @classmethod
    def check_project_exists(cls, value: str, info) -> str:
        """Validate synapse-backend project exists."""
        if not value:
            return value

        action = info.context['action']
        client = action.client
        try:
            client.get_project(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Error occurred while checking project exists.'))
        return value


@register_action
class UploadAction(Action):
    """Upload action class.

    Attrs:
        name (str): The name of the action.
        category (PluginCategory): The category of the action.
        method (RunMethod): The method to run of the action.

    Progress Categories:
        analyze_collection: The progress category for the analyze collection process.
        data_file_upload: The progress category for the upload process.
        generate_data_units: The progress category for the generate data units process.
        generate_tasks: The progress category for the generate tasks process.
        generate_ground_truths: The progress category for the generate ground truths process.
    """

    name = 'upload'
    category = PluginCategory.UPLOAD
    method = RunMethod.JOB
    progress_categories = {
        'analyze_collection': {
            'proportion': 5,
        },
        'upload_data_files': {
            'proportion': 35,
        },
        'generate_data_units': {
            'proportion': 20,
        },
        'generate_tasks': {
            'proportion': 20,
        },
        'generate_ground_truths': {
            'proportion': 20,
        },
    }

    def get_uploader(self, path):
        """Get uploader from entrypoint."""
        return self.entrypoint(self.run, path)

    def start(self) -> Dict:
        """Start upload process.

        Returns:
            Dict: The result of the upload process.
        """
        # Setup path object with path and storage.
        storage = self.client.get_storage(self.params['storage'])
        pathlib_cwd = get_pathlib(storage, self.params['path'])

        # Initialize uploader.
        uploader = self.get_uploader(pathlib_cwd)

        # Analyze Collection file specifications to determine the data structure for upload.
        self.run.set_progress(0, 1, category='analyze_collection')
        file_specification_skeleton = self._analyze_collection()
        self.run.set_progress(1, 1, category='analyze_collection')

        # Setup result dict.
        result = {}

        # Organize data according to Collection file specification structure.
        organized_files = uploader.handle_upload_files()
        if not self._validate_organized_files(file_specification_skeleton, organized_files):
            self.run.log_message('Validate organized files failed.')
            return result

        # Upload files to synapse-backend.
        organized_files_count = len(organized_files)
        if not organized_files_count:
            self.run.log_message('Files not found on the path.', context=Context.WARNING.value)
            return result

        self.run.set_progress(0, organized_files_count, category='upload_data_files')
        self.run.log_message('Uploading data files...')
        result['uploaded_files'] = self._upload_files(organized_files)
        self.run.set_progress(organized_files_count, organized_files_count, category='upload_data_files')
        self.run.log_message('Upload data files completed.')

        # Generate data units for the uploaded data.
        upload_result_count = len(result['uploaded_files'])
        if not upload_result_count:
            self.run.log_message('No files were uploaded.', context=Context.WARNING.value)
            return result

        self.run.set_progress(0, upload_result_count, category='generate_data_units')
        generated_data_units = self._generate_data_units(result['uploaded_files'])
        result['generated_data_units'] = generated_data_units
        self.run.set_progress(upload_result_count, upload_result_count, category='generate_data_units')

        # Setup task with uploaded synapse-backend data units.
        if not len(generated_data_units):
            self.run.log_message('No data units were generated.', context=Context.WARNING.value)
            return result

        self.run.set_progress(0, 1, category='generate_tasks')
        if self.config['options']['allow_generate_tasks'] and self.params['is_generate_tasks']:
            self.run.log_message('Generating tasks with data files...')
            self._generate_tasks(generated_data_units)
            self.run.log_message('Generating tasks completed')
        else:
            self.run.log_message('Generating tasks process has passed.')

        self.run.set_progress(1, 1, category='generate_tasks')

        # Generate ground truths for the uploaded data.
        # TODO: Need to add ground truths generation logic later.
        self.run.set_progress(0, 1, category='generate_ground_truths')
        if self.config['options']['allow_generate_ground_truths'] and self.params['is_generate_ground_truths']:
            self.run.log_message('Generating ground truths...')
            self._generate_ground_truths()
            self.run.log_message('Generating ground truths completed')
        else:
            self.run.log_message('Generating ground truths process has passed.')
        self.run.set_progress(1, 1, category='generate_ground_truths')

        return result

    def _analyze_collection(self) -> Dict:
        """Analyze Synapse Collection Specifications.

        Returns:
            Dict: The file specifications of the collection.
        """
        client = self.run.client
        collection_id = self.params['collection']
        collection = client.get_dataset(collection_id)
        return collection['file_specifications']

    def _validate_organized_files(self, file_specification_skeleton: Dict, organized_files: List) -> bool:
        """Validate organized files from Uploader."""
        return True

    def _upload_files(self, organized_files) -> List:
        """Upload files to synapse-backend.

        Returns:
            Dict: The result of the upload.
        """
        client = self.run.client
        collection_id = self.params['collection']
        upload_result = []
        organized_files_count = len(organized_files)
        current_progress = 0
        for organized_file in organized_files:
            upload_result.append(client.upload_data_file(organized_file, collection_id))
            self.run.set_progress(current_progress, organized_files_count, category='upload_data_files')
            current_progress += 1
        return upload_result

    def _generate_data_units(self, uploaded_files: List) -> List:
        """Generate data units for the uploaded data.

        TODO: make batch size configurable.

        Returns:
            Dict: The result of the generate data units process.
        """
        client = self.run.client

        generation_result = []
        current_progress = 0
        batches = get_batched_list(uploaded_files, 100)
        batches_count = len(batches)
        for batch in batches:
            generation_result.append(client.create_data_units(batch))
            self.run.set_progress(current_progress, batches_count, category='generate_data_units')
            current_progress += 1
        return generation_result

    def _generate_tasks(self, generated_data_units: List):
        """Setup task with uploaded synapse-backend data units.

        TODO: make batch size configurable.
        """

        # Prepare batches for processing
        client = self.run.client
        project_id = self.params['project']
        current_progress = 0

        # Generate tasks
        generated_data_units_count = len(generated_data_units)
        for data_units in generated_data_units:
            tasks_data = []
            for data_unit in data_units:
                task_data = {'project': project_id, 'data_unit': data_unit['id']}
                tasks_data.append(task_data)

            if tasks_data:
                client.create_tasks(tasks_data)

            self.run.set_progress(current_progress, generated_data_units_count, category='generate_tasks')
            current_progress += 1

    def _generate_ground_truths(self):
        """Generate ground truths for the uploaded data.

        TODO: Need to add ground truths generation logic later.
        """
