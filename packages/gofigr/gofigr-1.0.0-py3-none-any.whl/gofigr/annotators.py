"""\
Copyright (c) 2023, Flagstaff Solutions, LLC
All rights reserved.

"""
import json
import os
import re
import subprocess
import sys
from abc import ABC
from urllib.parse import unquote, urlparse

from gofigr import CodeLanguage
from gofigr.context import RevisionContext
from gofigr.databricks import get_dbutils

PATH_WARNING = "To fix this warning, you can manually specify the notebook name & path in the call to configure(). " \
               "Please see https://gofigr.io/docs/gofigr-python/latest/customization.html#notebook-name-path " \
               "for details."


class Annotator(ABC):
    """\
    Annotates figure revisions with pertinent information, such as cell code, variable values, etc.

    """
    def __init__(self, extension):
        self.extension = extension

    def annotate(self, revision):
        """
        Annotates the figure revision.

        :param revision: FigureRevision
        :return: annotated FigureRevision

        """
        return revision


class CellIdAnnotator(Annotator):
    """Annotates revisions with the ID of the Jupyter cell"""
    def annotate(self, revision):
        if revision.metadata is None:
            revision.metadata = {}

        try:
            cell_id = self.extension.cell.cell_id
        except AttributeError:
            cell_id = None

        revision.metadata['cell_id'] = cell_id

        return revision


class CellCodeAnnotator(Annotator):
    """"Annotates revisions with cell contents"""
    def annotate(self, revision):
        if self.extension.cell is not None:
            code = self.extension.cell.raw_cell
        else:
            code = "N/A"

        revision.data.append(revision.client.CodeData(name="Jupyter Cell",
                                                      language=CodeLanguage.PYTHON,
                                                      contents=code))
        return revision


class PipFreezeAnnotator(Annotator):
    """Annotates revisions with the output of pip freeze"""
    def __init__(self, extension, cache=True):
        """\
        :param extension: the GoFigr Jupyter extension
        :param cache: if True, will only run pip freeze once and cache the output
        """
        super().__init__(extension)
        self.cache = cache
        self.cached_output = None

    def annotate(self, revision):
        if self.cache and self.cached_output:
            output = self.cached_output
        else:
            try:
                output = subprocess.check_output(["pip", "freeze"]).decode('ascii')
                self.cached_output = output
            except subprocess.CalledProcessError as e:
                output = e.output

        revision.data.append(revision.client.TextData(name="pip freeze", contents=output))
        return revision


class SystemAnnotator(Annotator):
    """Annotates revisions with the OS version"""
    def annotate(self, revision):
        try:
            output = subprocess.check_output(["uname", "-a"]).decode('ascii')
        except subprocess.CalledProcessError as e:
            output = e.output

        revision.data.append(revision.client.TextData(name="System Info", contents=output))
        return revision


NOTEBOOK_PATH = "notebook_path"
NOTEBOOK_NAME = "notebook_name"
NOTEBOOK_URL = "url"
NOTEBOOK_KERNEL = "kernel"
PYTHON_VERSION = "python_version"
BACKEND_NAME = "backend"


_ACTIVE_TAB_TITLE = "active_tab_title"


def _parse_path_from_tab_title(title):
    """Parses out the notebook path from the tab/widget title"""
    for line in title.splitlines(keepends=False):
        m = re.match(r'Path:\s*(.*)\s*', line)
        if m:
            return m.group(1)
    return None


class NotebookMetadataAnnotator(Annotator):
    """"Annotates revisions with notebook metadata, including filename & path, as well as the full URL"""
    def parse_from_databricks(self):
        """Returns notebook path if running in Databricks"""
        try:
            # pylint: disable=undefined-variable
            context = get_dbutils(self.extension.shell).notebook.entry_point.getDbutils().notebook().getContext()
            nb = context.notebookPath().get()
            return {NOTEBOOK_PATH: nb, NOTEBOOK_NAME: os.path.basename(nb)}
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def parse_from_vscode(self):
        """Returns notebook path if running in VSCode"""
        if self.extension.cell is None or self.extension.cell.cell_id is None:
            return None
        elif "vscode-notebook-cell:" not in self.extension.cell.cell_id:
            return None

        m = re.match(r'^vscode-notebook-cell:(.*)#.*$', unquote(self.extension.cell.cell_id))
        if m is None:
            return None

        notebook_path = m.group(1)
        notebook_name = os.path.basename(notebook_path)

        return {NOTEBOOK_PATH: notebook_path,
                NOTEBOOK_NAME: notebook_name}

    def try_get_metadata(self):
        """Infers the notebook path & name using currently available metadata if possible, returning None otherwise"""
        try:
            return self.parse_metadata(error=False)
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def _parse_from_proxy(self, meta, error):
        if 'url' not in meta and _ACTIVE_TAB_TITLE not in meta:
            if error:
                raise RuntimeError("No URL found in Notebook metadata")
            else:
                return None

        notebook_name = None

        # Try parsing the name from the title first
        if _ACTIVE_TAB_TITLE in meta and meta[_ACTIVE_TAB_TITLE] is not None:
            notebook_name = _parse_path_from_tab_title(meta[_ACTIVE_TAB_TITLE])

        # If that doesn't work, try the URL
        if notebook_name is None:
            notebook_name = unquote(urlparse(meta['url']).path.rsplit('/', 1)[-1])

        notebook_dir = self.extension.shell.starting_dir
        full_path = None

        for candidate_path in [os.path.join(notebook_dir, notebook_name),
                               os.path.join(notebook_dir, os.path.basename(notebook_name)),
                               os.path.join(os.path.dirname(notebook_dir), notebook_name),
                               os.path.join(os.path.dirname(notebook_dir), os.path.basename(notebook_name))]:
            if os.path.exists(candidate_path):
                full_path = candidate_path
                break

        if full_path is None:
            full_path = os.path.join(notebook_dir, notebook_name)  # might still be helpful, even if slightly incorrect
            print(f"The inferred path for the notebook does not exist: {full_path}. {PATH_WARNING}", file=sys.stderr)

        return {NOTEBOOK_PATH: full_path,
                NOTEBOOK_NAME: notebook_name,
                NOTEBOOK_URL: meta.get('url')}

    def parse_metadata(self, error=True):
        """
        Infers the notebook path & name from metadata passed through the WebSocket (if available)

        :param error: if True, will raise an error if metadata is not available
        """
        vsc_meta = self.parse_from_vscode()
        if vsc_meta is not None:
            return vsc_meta

        db_meta = self.parse_from_databricks()
        if db_meta is not None:
            return db_meta

        # At this point the metadata needs to come from the JavaScript proxy
        meta = self.extension.notebook_metadata
        if meta is None and error:
            raise RuntimeError("No Notebook metadata available")
        elif meta is None:
            return None

        return self._parse_from_proxy(meta, error)

    def annotate(self, revision):
        if revision.metadata is None:
            revision.metadata = {}

        try:
            if NOTEBOOK_NAME not in revision.metadata or NOTEBOOK_PATH not in revision.metadata:
                revision.metadata.update(self.parse_metadata())

            full_path = revision.metadata.get(NOTEBOOK_PATH)
            if full_path and os.path.exists(full_path):
                revision.data += [revision.client.FileData.read(full_path)]

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"GoFigr could not automatically obtain the name of the currently"
                  f" running notebook. {PATH_WARNING} Details: {e}",
                  file=sys.stderr)

            revision.metadata[NOTEBOOK_NAME] = "N/A"
            revision.metadata[NOTEBOOK_PATH] = "N/A"

        return revision


class NotebookNameAnnotator(NotebookMetadataAnnotator):
    """(Deprecated) Annotates revisions with notebook name & path"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("NotebookNameAnnotator is deprecated. Please use NotebookMetadataAnnotator", file=sys.stderr)


class EnvironmentAnnotator(Annotator):
    """Annotates revisions with the python version & the kernel info"""
    def annotate(self, revision):
        if revision.metadata is None:
            revision.metadata = {}

        revision.metadata[NOTEBOOK_KERNEL] = sys.executable
        revision.metadata[PYTHON_VERSION] = sys.version

        return revision


class BackendAnnotator(Annotator):
    """Annotates revisions with the python version & the kernel info"""
    def annotate(self, revision):
        if revision.metadata is None:
            revision.metadata = {}

        context = RevisionContext.get(revision)
        revision.metadata[BACKEND_NAME] = context.backend.get_backend_name() if context and context.backend else "N/A"

        return revision


class HistoryAnnotator(Annotator):
    """Annotates revisions with IPython execution history"""
    def annotate(self, revision):
        context = RevisionContext.get(revision)

        if not hasattr(context.extension.shell, 'history_manager'):
            return revision

        hist = context.extension.shell.history_manager
        if hist is None:
            return revision

        revision.data.append(revision.client.CodeData(name="IPython history",
                                                      language="python",
                                                      format="jupyter-history/json",
                                                      contents=json.dumps(hist.input_hist_raw)))
        return revision
