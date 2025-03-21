"""A collection of useful functions.

The template and this example uses Google style docstrings as described at:
https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

"""

import json
import os

import nbformat
from nbformat import NotebookNode


def _read_notebook(fp: str) -> NotebookNode:
    return nbformat.read(fp, as_version=nbformat.NO_CONVERT)  # type: ignore


def notebook_to_cms(
    notebook_filename: str,
    endpoint: str,
    notebook_folder: str = "",
    display_name: str = "",
) -> dict[str, str]:
    r"""Sends all the markdown content of a notebook to a CMS endpoint.

    This function can be executed within the notebook it gets the markdown content from, \
    but the notebook filename always has to be explicitly passed.

    The CMS endpoint has to satisfy two constraints:
    * It must accept post requests with fields *id*, *displayName* and *markdown*.
    * The response body must have a key *_id* whose value should be \
    the unique identifier of the created content in the CMS.

    On the first successfull request, an empty string is sent as *id*,
    and the *_id* in the response is stored in a JSON file \
    (created in the same directory as the notebook file). \
    On subsequent requests, the stored value is sent as *id*.

    Args:
        notebook_filename (str): The name of the notebook file.
        endpoint (str): The URL of the CMS endpoint.
        notebook_folder (str): Ignore this parameter when executing the function from \
        the notebook containing the markdown content. \
        Sets a custom base directory (absolute path) containing the notebook file.
        display_name (str): Send a custom *displayName* value to the CMS endpoint.

    Returns:
        (dict): The response from the CMS endpoint.
    """
    if notebook_folder:
        os.chdir(notebook_folder)
    else:
        os.chdir(os.getcwd())

    basename = os.path.splitext(notebook_filename)[0]
    json_filename = basename + ".json"

    _id = ""
    if os.path.exists(json_filename):
        with open(json_filename) as file:
            _id = json.load(file)["_id"]

    if not display_name:
        display_name = basename.replace("_", " ").title()

    markdown = ""
    if os.path.exists(notebook_filename):
        notebook = _read_notebook(notebook_filename)
        markdown = "\n\n".join(
            cell.source for cell in notebook.cells if cell.cell_type == "markdown"
        )

    endpoint = endpoint

    request_data = {"id": _id, "displayName": display_name, "markdown": markdown}

    return request_data
