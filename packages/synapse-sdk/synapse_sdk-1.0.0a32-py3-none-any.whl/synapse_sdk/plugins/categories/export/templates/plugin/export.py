import json
from pathlib import Path

import requests


def export(run, input_dataset, path_root, **params):
    """Executes the export task.

    Args:
        run : Execution object
        input_dataset (generator):
            - data (dict): dm_schema_data information.
            - files (dict): File information. Includes file URL, original file path, metadata, etc.
            - id (int): ground_truth ID
        path_root : pathlib object, the path to export
        **params: Additional parameters

    Returns:
        dict: Result
    """

    path_root.mkdir(parents=True, exist_ok=True)
    run.log_message('Starting export process.')

    # results contains all information fetched through the list API.
    # example:
    #   params.get('results', [])

    save_original_file_flag = params.get('save_original_file')
    errors_json_file_list = []
    errors_original_file_list = []

    # Path to save JSON files
    json_output_path = path_root / 'json'
    json_output_path.mkdir(parents=True, exist_ok=True)

    # Path to save original files
    origin_files_output_path = path_root / 'origin_files'
    origin_files_output_path.mkdir(parents=True, exist_ok=True)

    total = params['count']
    # progress init
    run.set_progress(0, total, category='dataset_conversion')
    for no, input_data in enumerate(input_dataset, start=1):
        run.set_progress(no, total, category='dataset_conversion')
        if no == 1:
            run.log_message('Converting dataset.')
        preprocessed_data = before_convert(input_data)
        converted_data = convert_data(preprocessed_data)
        final_data = after_convert(converted_data)

        # Call if original file extraction is needed
        if save_original_file_flag:
            if no == 1:
                run.log_message('Saving original file.')
            save_original_file(final_data, origin_files_output_path, errors_original_file_list)

        # Extract data as JSON files
        if no == 1:
            run.log_message('Saving json file.')
        save_as_json(final_data, json_output_path, errors_json_file_list)

    run.end_log()

    # Save error list files
    if len(errors_json_file_list) > 0 or len(errors_original_file_list) > 0:
        export_error_file = {'json_file_name': errors_json_file_list, 'origin_file_name': errors_original_file_list}
        with (path_root / 'error_file_list.json').open('w', encoding='utf-8') as f:
            json.dump(export_error_file, f, indent=4, ensure_ascii=False)

    return {'export_path': str(path_root)}


def convert_data(data):
    """Converts the data."""
    return data


def before_convert(data):
    """Preprocesses the data before conversion."""
    return data


def after_convert(data):
    """Post-processes the data after conversion."""
    return data


def get_original_file_pathlib(files):
    """Retrieve the original file path from the given file information.

    Args:
        files (dict): A dictionary containing file information, including file URL,
                      original file path, metadata, etc.

    Returns:
        pathlib.Path: The original file path extracted from the metadata.
    """
    return Path(next(iter(files.values()))['meta']['path_original'])


def save_original_file(result, base_path, error_file_list):
    """Saves the original file.

    Args:
        result (dict): API response data containing file information.
        base_path (Path): The directory where the file will be saved.
        error_file_list (list): A list to store error files.
    """
    file_url = next(iter(result['files'].values()))['url']
    file_name = get_original_file_pathlib(result['files']).name
    response = requests.get(file_url)
    try:
        with (base_path / file_name).open('wb') as file:
            file.write(response.content)
    except Exception as e:
        error_file_list.append([file_name, str(e)])


def save_as_json(result, base_path, error_file_list):
    """Saves the data as a JSON file.

    Args:
        result (dict): API response data containing file information.
        base_path (Path): The directory where the file will be saved.
        error_file_list (list): A list to store error files.
    """
    # Default save file name: original file name
    file_name = get_original_file_pathlib(result['files']).stem
    json_data = result['data']
    try:
        with (base_path / f'{file_name}.json').open('w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        error_file_list.append([f'{file_name}.json', str(e)])
