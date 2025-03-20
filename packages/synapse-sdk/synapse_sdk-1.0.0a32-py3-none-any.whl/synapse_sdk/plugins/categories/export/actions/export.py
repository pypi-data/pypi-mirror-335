from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.i18n import gettext as _
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.utils.storage import get_pathlib


class ExportParams(BaseModel):
    storage: int
    save_original_file: bool = True
    path: str
    ground_truth_dataset_version: int
    filter: dict

    @field_validator('storage')
    @staticmethod
    def check_storage_exists(value, info):
        action = info.context['action']
        client = action.client
        try:
            client.get_storage(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get storage from Synapse backend.'))
        return value

    @field_validator('ground_truth_dataset_version')
    @staticmethod
    def check_ground_truth_dataset_version_exists(value, info):
        action = info.context['action']
        client = action.client
        try:
            client.get_ground_truth_version(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get Ground Truth dataset version.'))
        return value


@register_action
class ExportAction(Action):
    name = 'export'
    category = PluginCategory.EXPORT
    method = RunMethod.JOB
    params_model = ExportParams
    progress_categories = {
        'dataset_conversion': {
            'proportion': 100,
        }
    }

    def get_dataset(self, results):
        """Get dataset for export."""
        for result in results:
            yield {
                'data': result['data'],
                'files': result['data_unit']['files'],
                'id': result['ground_truth'],
            }

    def get_filtered_results(self):
        """Get filtered ground truth events."""
        self.params['filter']['ground_truth_dataset_versions'] = self.params['ground_truth_dataset_version']
        filters = {'expand': 'data', **self.params['filter']}

        try:
            gt_dataset_events_list = self.client.list_ground_truth_events(params=filters, list_all=True)
            results = gt_dataset_events_list[0]
            count = gt_dataset_events_list[1]
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get Ground Truth dataset.'))
        return results, count

    def start(self):
        self.params['results'], self.params['count'] = self.get_filtered_results()
        dataset = self.get_dataset(self.params['results'])

        storage = self.client.get_storage(self.params['storage'])
        pathlib_cwd = get_pathlib(storage, self.params['path'])
        return self.entrypoint(self.run, dataset, pathlib_cwd, **self.params)
