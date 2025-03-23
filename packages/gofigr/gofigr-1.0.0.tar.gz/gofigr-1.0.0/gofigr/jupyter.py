"""\
Copyright (c) 2022, Flagstaff Solutions, LLC
All rights reserved.

"""
# pylint: disable=cyclic-import, no-member, global-statement, protected-access, wrong-import-order, ungrouped-imports
# pylint: disable=too-many-locals

import inspect
import io
import json
import os
import pickle
import sys
from collections import namedtuple
from functools import wraps
from pathlib import Path
from uuid import UUID

import PIL
import six

import gofigr.databricks
from gofigr import GoFigr, API_URL, UnauthorizedError
from gofigr.annotators import CellIdAnnotator, SystemAnnotator, CellCodeAnnotator, \
    PipFreezeAnnotator, NotebookMetadataAnnotator, EnvironmentAnnotator, BackendAnnotator, HistoryAnnotator, \
    NOTEBOOK_NAME
from gofigr.backends import get_backend, GoFigrBackend
from gofigr.backends.matplotlib import MatplotlibBackend
from gofigr.backends.plotly import PlotlyBackend
from gofigr.context import RevisionContext
from gofigr.proxy import run_proxy_async, get_javascript_loader
from gofigr.profile import MeasureExecution
from gofigr.watermarks import DefaultWatermark
from gofigr.widget import DetailedWidget, StartupWidget

try:
    from IPython.core.display_functions import display
except ModuleNotFoundError:
    from IPython.core.display import display

PY3DMOL_PRESENT = False
if sys.version_info >= (3, 8):
    try:
        import py3Dmol  # pylint: disable=unused-import
        from gofigr.backends.py3dmol import Py3DmolBackend
        PY3DMOL_PRESENT = True
    except ModuleNotFoundError:
        pass

PLOTNINE_PRESENT = False
try:
    import plotnine # pylint: disable=unused-import
    from gofigr.backends.plotnine import PlotnineBackend
    PLOTNINE_PRESENT = True
except ModuleNotFoundError:
    pass


DISPLAY_TRAP = None


def _mark_as_published(fig):
    """Marks the figure as published so that it won't be re-published again."""
    fig._gf_is_published = True
    return fig


def suppress(fig):
    """Suppresses the figure from being auto-published. You can still publish it by calling publish()."""
    fig._gf_is_suppressed = True
    return fig


def is_suppressed(fig):
    """Determines if the figure is suppressed from publication"""
    return getattr(fig, "_gf_is_suppressed", False)


def _is_published(fig):
    """Returns True iff the figure has already been published"""
    return getattr(fig, "_gf_is_published", False)


class GfDisplayPublisher:
    """\
    Custom IPython DisplayPublisher which traps all calls to publish() (e.g. when display(...) is called).

    """
    def __init__(self, pub):
        """

        :param pub: Publisher to wrap around. We delegate all calls to this publisher unless trapped.
        """
        self.pub = pub

    def publish(self, data, *args, **kwargs):
        """
        IPython calls this method whenever it needs data displayed. Our function traps the call
        and calls DISPLAY_TRAP instead, giving it an option to suppress the figure from being displayed.

        We use this trap to publish the figure if auto_publish is True. Suppression is useful
        when we want to show a watermarked version of the figure, and prevents it from being showed twice (once
        with the watermark inside the trap, and once without in the originating call).

        :param data: dictionary of mimetypes -> data
        :param args: implementation-dependent
        :param kwargs: implementation-dependent
        :return: None

        """

        # Python doesn't support assignment to variables in closure scope, so we use a mutable list instead
        is_display_suppressed = [False]
        def suppress_display():
            is_display_suppressed[0] = True

        if DISPLAY_TRAP is not None:
            trap = DISPLAY_TRAP
            with SuppressDisplayTrap():
                trap(data, suppress_display=suppress_display)

        if not is_display_suppressed[0]:
            self.pub.publish(data, *args, **kwargs)

    def __getattr__(self, item):
        """\
        Delegates to self.pub

        :param item:
        :return:
        """
        if item == "pub":
            return super().__getattribute__(item)

        return getattr(self.pub, item)

    def __setattr__(self, key, value):
        """\
        Delegates to self.pub

        :param key:
        :param value:
        :return:
        """
        if key == "pub":
            super().__setattr__(key, value)

        return setattr(self.pub, key, value)

    def clear_output(self, *args, **kwargs):
        """IPython's clear_output. Defers to self.pub"""
        return self.pub.clear_output(*args, **kwargs)


class SuppressDisplayTrap:
    """\
    Context manager which temporarily suspends all display traps.
    """
    def __init__(self):
        self.trap = None

    def __enter__(self):
        global DISPLAY_TRAP
        self.trap = DISPLAY_TRAP
        DISPLAY_TRAP = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        global DISPLAY_TRAP
        DISPLAY_TRAP = self.trap
        self.trap = None


# pylint: disable=too-many-instance-attributes
class _GoFigrExtension:
    """\
    Implements the main Jupyter extension functionality. You will not want to instantiate this class directly.
    Instead, please call get_extension().
    """
    def __init__(self, ip,
                 auto_publish=False,
                 notebook_metadata=None,
                 configured=False,
                 loader_shown=False):
        """\

        :param ip: iPython shell instance
        :param auto_publish: whether to auto-publish figures
        :param pre_run_hook: function to use as a pre-run hook
        :param post_execute_hook: function to use as a post-execute hook
        :param notebook_metadata: information about the running notebook, as a key-value dictionary

        """
        self.shell = ip
        self.auto_publish = auto_publish
        self.cell = None
        self.proxy = None
        self.loader_shown = loader_shown
        self.configured = configured
        if notebook_metadata is None:
            self.notebook_metadata = NotebookMetadataAnnotator(self).try_get_metadata()
        else:
            self.notebook_metadata = notebook_metadata

        self.gf = None  # active GF object
        self.workspace = None  # current workspace
        self._analysis = None  # current analysis
        self.publisher = None  # current Publisher instance
        self.wait_for_metadata = None  # callable which waits for metadata to become available

        self.deferred_revisions = []

    @property
    def is_ready(self):
        """True if the extension has been configured and ready for use."""
        return self.configured and self.notebook_metadata is not None

    @property
    def analysis(self):
        """Gets the current analysis"""
        if isinstance(self._analysis, NotebookName):
            meta = NotebookMetadataAnnotator(self).parse_metadata()
            self._analysis = self.workspace.get_analysis(name=Path(meta[NOTEBOOK_NAME]).stem, create=True)
            self._analysis.fetch()

        return self._analysis

    @analysis.setter
    def analysis(self, value):
        self._analysis = value

    def display_trap(self, data, suppress_display):
        """\
         Called whenever *any* code inside the Jupyter session calls display().
        :param data: dictionary of MIME types
        :param suppress_display: callable with no arguments. Call to prevent the originating figure from being shown.
        :return: None

        """
        if self.auto_publish:
            self.publisher.auto_publish_hook(self, data, suppress_display)

    def add_to_deferred(self, rev):
        """\
        Adds a revision to a list of deferred revisions. Such revisions will be annotated in the post_run_cell
        hook, and re-saved.

        This functionality exists because it's possible to load the GoFigr extension and publish figures in the same
        cell, in which case GoFigr will not receive the pre_run_cell hook and will not have access to cell information
        when the figure is published. This functionality allows us to obtain the cell information after it's run
        (in the post_run_cell hook), re-run annotators, and update the figure with full annotations.

        :param rev: revision to defer
        :return: None
        """
        if rev not in self.deferred_revisions:
            self.deferred_revisions.append(rev)

    def check_config(self):
        """Ensures the plugin has been configured for use"""
        if not self.configured:
            raise RuntimeError("GoFigr not configured. Please call configure() first.")

    def pre_run_cell(self, info):
        """\
        Default pre-run cell hook.

        :param info: Cell object
        :return:None

        """
        self.cell = info

    def _get_metadata_from_proxy(self, result):
        if self.configured and not self.loader_shown and "_VSCODE" not in result.info.raw_cell:
            self.proxy, self.wait_for_metadata = run_proxy_async(self.gf, proxy_callback)

            with SuppressDisplayTrap():
                display(get_javascript_loader(self.gf, self.proxy))
                self.loader_shown = True

        if self.notebook_metadata is None and self.wait_for_metadata is not None:
            self.wait_for_metadata()
            self.wait_for_metadata = None


    def post_run_cell(self, result):
        """Post run cell hook.

        :param result: ExecutionResult
        :return: None

        """
        self.cell = result.info

        if self.notebook_metadata is None:
            self._get_metadata_from_proxy(result)

        while len(self.deferred_revisions) > 0:
            rev = self.deferred_revisions.pop(0)
            rev = self.publisher.annotate(rev)
            rev.save(silent=True)

        self.cell = None

    def _register_handler(self, event_name, handler):
        """Inserts a handler at the beginning of the list while avoiding double-insertions"""
        handlers = [handler]
        for hnd in self.shell.events.callbacks[event_name]:
            self.shell.events.unregister(event_name, hnd)
            if hnd != handler:  # in case it's already registered, skip it
                handlers.append(hnd)

        for hnd in handlers:
            self.shell.events.register(event_name, hnd)

    def unregister(self):
        """\
        Unregisters all hooks, effectively disabling the plugin.

        """
        try:
            self.shell.events.unregister('pre_run_cell', self.pre_run_cell)
        except ValueError:
            pass

        try:
            self.shell.events.unregister('post_run_cell', self.post_run_cell)
        except ValueError:
            pass

    def register_hooks(self):
        """\
        Register all hooks with Jupyter.

        :return: None
        """
        global DISPLAY_TRAP
        DISPLAY_TRAP = self.display_trap

        self._register_handler('pre_run_cell', self.pre_run_cell)
        self._register_handler('post_run_cell', self.post_run_cell)

        native_display_publisher = self.shell.display_pub
        if not isinstance(native_display_publisher, GfDisplayPublisher):
            self.shell.display_pub = GfDisplayPublisher(native_display_publisher)


_GF_EXTENSION = None  # GoFigrExtension global


def require_configured(func):
    """\
    Decorator which throws an exception if configure() has not been called yet.

    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if _GF_EXTENSION is None:
            raise RuntimeError("Please load the extension: %load_ext gofigr")
        _GF_EXTENSION.check_config()

        return func(*args, **kwargs)

    return wrapper


@require_configured
def get_extension():
    """Returns the GoFigr Jupyter extension instance"""
    return _GF_EXTENSION


def _load_ipython_extension(ip):
    """\
    Loads the Jupyter extension. Aliased to "load_ipython_extension" (no leading underscore) in the main init.py file.

    :param ip: IPython shell
    :return: None

    """
    global _GF_EXTENSION
    if _GF_EXTENSION is not None:
        _GF_EXTENSION.unregister()

    _GF_EXTENSION = _GoFigrExtension(ip)
    _GF_EXTENSION.register_hooks()

    try:
        configure()
    except Exception as e:  # pylint: disable=broad-exception-caught
        if "auth" in str(e).lower() and "failed" in str(e).lower():
            print("GoFigr authentication failed. Please manually call configure(api_key=<YOUR API KEY>).",
                  file=sys.stderr)
        else:
            print(f"Could not automatically configure GoFigr. Please call configure() manually. Error: {e}",
                  file=sys.stderr)

    for name in ['configure', 'publish', "FindByName", "ApiId", "NotebookName", "get_extension"]:
        ip.user_ns[name] = globals()[name]


def parse_uuid(val):
    """\
    Attempts to parse a UUID, returning None if input is not a valid UUID.

    :param val: value to parse
    :return: UUID (as a string) or None

    """
    try:
        return str(UUID(val))
    except ValueError:
        return None


ApiId = namedtuple("ApiId", ["api_id"])

class FindByName:
    """\
    Used as argument to configure() to specify that we want to find an analysis/workspace by name instead
    of using an API ID
    """
    def __init__(self, name, description=None, create=False):
        self.name = name
        self.description = description
        self.create = create

    def __repr__(self):
        return f"FindByName(name={self.name}, description={self.description}, create={self.create})"


class NotebookName:
    """\
    Used as argument to configure() to specify that we want the analysis name to default to the name of the notebook
    """
    def __repr__(self):
        return "NotebookName"


def parse_model_instance(model_class, value, find_by_name):
    """\
    Parses a model instance from a value, e.g. the API ID or a name.

    :param model_class: class of the model, e.g. gf.Workspace
    :param value: value to parse into a model instance
    :param find_by_name: callable to find the model instance by name
    :return: model instance

    """
    if isinstance(value, model_class):
        return value
    elif isinstance(value, str):
        return model_class(api_id=value)
    elif isinstance(value, ApiId):
        return model_class(api_id=value.api_id)
    elif isinstance(value, FindByName):
        return find_by_name(value)
    else:
        return ValueError(f"Unsupported target specification: {value}. Please specify an API ID, or use FindByName.")


DEFAULT_ANNOTATORS = (NotebookMetadataAnnotator, EnvironmentAnnotator, CellIdAnnotator, CellCodeAnnotator,
                      SystemAnnotator, PipFreezeAnnotator, BackendAnnotator, HistoryAnnotator)
DEFAULT_BACKENDS = (MatplotlibBackend, PlotlyBackend)
if PY3DMOL_PRESENT:
    # pylint: disable=possibly-used-before-assignment
    DEFAULT_BACKENDS = DEFAULT_BACKENDS + (Py3DmolBackend,)

if PLOTNINE_PRESENT:
    # pylint: disable=possibly-used-before-assignment
    DEFAULT_BACKENDS = (PlotnineBackend,) + DEFAULT_BACKENDS


# pylint: disable=too-many-instance-attributes
class Publisher:
    """\
    Publishes revisions to the GoFigr server.
    """
    # pylint: disable=too-many-arguments
    def __init__(self,
                 gf,
                 annotators,
                 backends,
                 watermark=None,
                 show_watermark=True,
                 image_formats=("png", "eps", "svg"),
                 interactive=True,
                 default_metadata=None,
                 clear=True,
                 save_pickle=True,
                 widget_class=DetailedWidget):
        """

        :param gf: GoFigr instance
        :param annotators: revision annotators
        :param backends: figure backends, e.g. MatplotlibBackend
        :param watermark: watermark generator, e.g. QRWatermark()
        :param show_watermark: True to show watermarked figures instead of original.
        False to always display the unmodified figure. Default True.
        :param image_formats: image formats to save by default
        :param interactive: whether to publish figure HTML if available
        :param clear: whether to close the original figures after publication. If False, Jupyter will display
        both the input figure and the watermarked output. Default behavior is to close figures.
        :param save_pickle: if True, will save the figure in pickle format in addition to any of the image formats
        :param widget_class: Widget type to show, e.g. DetailedWidget or CompactWidget. It will appear below the
        published figure

        """
        self.gf = gf
        self.watermark = watermark or DefaultWatermark()
        self.show_watermark = show_watermark
        self.annotators = annotators
        self.backends = backends
        self.image_formats = image_formats
        self.interactive = interactive
        self.clear = clear
        self.default_metadata = default_metadata
        self.save_pickle = save_pickle
        self.widget_class = widget_class

    def auto_publish_hook(self, extension, data, suppress_display=None):
        """\
        Hook for automatically publishing figures without an explicit call to publish().

        :param extension: GoFigrExtension instance
        :param data: data being published. This will usually be a dictionary of mime formats.
        :param native_publish: callable which will publish the figure using the native backend

        :return: None
        """
        for backend in self.backends:
            compatible_figures = list(backend.find_figures(extension.shell, data))
            for fig in compatible_figures:
                if not _is_published(fig) and not is_suppressed(fig):
                    self.publish(fig=fig, backend=backend, suppress_display=suppress_display)

            if len(compatible_figures) > 0:
                break

    @staticmethod
    def _check_analysis(ext):
        if ext.analysis is None:
            print("You did not specify an analysis to publish under. Please call "
                  "configure(...) and specify one. See "
                  "https://gofigr.io/docs/gofigr-python/latest/gofigr.html#gofigr.jupyter.configure.",
                  file=sys.stderr)
            return None
        elif isinstance(ext.analysis, NotebookName):
            print("Your analysis is set to the name of this notebook, but the name could "
                  "not be inferred. Please call "
                  "configure(...) and specify the analysis manually. See "
                  "https://gofigr.io/docs/gofigr-python/latest/gofigr.html#gofigr.jupyter.configure.",
                  file=sys.stderr)
            return None
        else:
            return ext.analysis

    @staticmethod
    def _resolve_target(gf, fig, target, backend):
        ext = get_extension()
        analysis = Publisher._check_analysis(ext)
        if analysis is None:
            return None

        if target is None:
            # Try to get the figure's title
            fig_name = backend.get_title(fig)
            if fig_name is None:
                print("Your figure doesn't have a title and will be published as 'Anonymous Figure'. "
                      "To avoid this warning, set a figure title or manually call publish() with a target figure. "
                      "See https://gofigr.io/docs/gofigr-python/latest/start.html#publishing-your-first-figure for "
                      "an example.", file=sys.stderr)
                fig_name = "Anonymous Figure"

            sys.stdout.flush()
            return analysis.get_figure(fig_name, create=True)
        else:
            return parse_model_instance(gf.Figure,
                                        target,
                                        lambda search: analysis.get_figure(name=search.name,
                                                                           description=search.description,
                                                                           create=search.create))

    def _get_pickle_data(self, gf, fig):
        if not self.save_pickle:
            return []

        try:
            bio = io.BytesIO()
            pickle.dump(fig, bio)
            bio.seek(0)

            return [gf.ImageData(name="figure", format="pickle",
                                 data=bio.getvalue(),
                                 is_watermarked=False)]
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"WARNING: We could not obtain the figure in pickle format: {e}", file=sys.stderr)
            return []

    def _get_image_data(self, gf, backend, fig, rev, image_options):
        """\
        Extracts ImageData in various formats.

        :param gf: GoFigr instance
        :param backend: backend to use
        :param fig: figure object
        :param rev: Revision object
        :param image_options: backend-specific parameters
        :return: tuple of: list of ImageData objects, watermarked image to display

        """
        if image_options is None:
            image_options = {}

        image_to_display = None
        image_data = []
        for fmt in self.image_formats:
            if fmt.lower() not in backend.get_supported_image_formats():
                continue

            if fmt.lower() == "png":
                img = PIL.Image.open(io.BytesIO(backend.figure_to_bytes(fig, fmt, image_options)))
                img.load()
                watermarked_img = self.watermark.apply(img, rev)
            else:
                watermarked_img = None

            # First, save the image without the watermark
            try:
                image_data.append(gf.ImageData(name="figure",
                                               format=fmt,
                                               data=backend.figure_to_bytes(fig, fmt, image_options),
                                               is_watermarked=False))
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"WARNING: We could not obtain the figure in {fmt.upper()} format: {e}", file=sys.stderr)
                continue

            # Now, save the watermarked version (if available)
            if watermarked_img is not None:
                bio = io.BytesIO()
                watermarked_img.save(bio, format=fmt)
                img_data = gf.ImageData(name="figure", format=fmt, data=bio.getvalue(),
                                        is_watermarked=True)
                image_data.append(img_data)

                if fmt.lower() == 'png':
                    image_to_display = img_data

        if self.interactive and backend.is_interactive(fig):
            image_data.append(gf.ImageData(name="figure", format="html",
                                           data=backend.figure_to_html(fig).encode('utf-8'),
                                           is_watermarked=False))

            wfig = backend.add_interactive_watermark(fig, rev, self.watermark)
            html_with_watermark = gf.ImageData(name="figure", format="html",
                                               data=backend.figure_to_html(wfig).encode('utf-8'),
                                               is_watermarked=True)
            image_data.append(html_with_watermark)
            image_to_display = wfig  # display the native Figure

        image_data.extend(self._get_pickle_data(gf, fig))

        return image_data, image_to_display

    def annotate(self, rev):
        """
        Annotates a FigureRevision using self.annotators.
        :param rev: revision to annotate
        :return: annotated revision

        """
        for annotator in self.annotators:
            with MeasureExecution(annotator.__class__.__name__):
                annotator.annotate(rev)
        return rev

    def _infer_figure_and_backend(self, fig, backend):
        """\
        Given a figure and a backend where one of the values could be null, returns a complete set
        of a figure to publish and a matching backend.

        :param fig: figure to publish. None to publish the default for the backend
        :param backend: backend to use. If None, will infer from figure
        :return: tuple of figure and backend
        """
        if fig is None and backend is None:
            raise ValueError("You did not specify a figure to publish.")
        elif fig is not None and backend is not None:
            return fig, backend
        elif fig is None and backend is not None:
            fig = backend.get_default_figure()

            if fig is None:
                raise ValueError("You did not specify a figure to publish, and the backend does not have "
                                 "a default.")
        else:
            backend = get_backend(fig, self.backends)

        return fig, backend

    def _prepare_files(self, gf, files):
        if not isinstance(files, dict):
            files = {os.path.basename(p): p for p in files}

        data = []
        for name, filelike in files.items():
            if isinstance(filelike, str): # path
                with open(filelike, 'rb') as f:
                    data.append(gf.FileData(data=f.read(), name=name, path=filelike))
            else:  # stream
                data.append(gf.FileData(data=filelike.read(), name=name, path=None))

        return data

    def publish(self, fig=None, target=None, gf=None, dataframes=None, metadata=None,
                backend=None, image_options=None, suppress_display=None, files=None):
        """\
        Publishes a revision to the server.

        :param fig: figure to publish. If None, we'll use plt.gcf()
        :param target: Target figure to publish this revision under. Can be a gf.Figure instance, an API ID, \
        or a FindByName instance.
        :param gf: GoFigure instance
        :param dataframes: dictionary of dataframes to associate & publish with the figure
        :param metadata: metadata (JSON) to attach to this revision
        usage this will cause Jupyter to print the whole object which we don't want.
        :param backend: backend to use, e.g. MatplotlibBackend. If None it will be inferred automatically based on \
        figure type
        :param image_options: backend-specific params passed to backend.figure_to_bytes
        :param suppress_display: if used in an auto-publish hook, this will contain a callable which will
        suppress the display of this figure using the native IPython backend.
        :param files: either (a) list of file paths or (b) dictionary of name to file path/file obj

        :return: FigureRevision instance

        """
        # pylint: disable=too-many-branches
        ext = get_extension()
        gf = gf if gf is not None else ext.gf
        fig, backend = self._infer_figure_and_backend(fig, backend)

        with MeasureExecution("Resolve target"):
            target = self._resolve_target(gf, fig, target, backend)
            if getattr(target, 'revisions', None) is None:
                target.fetch()

        combined_meta = self.default_metadata if self.default_metadata is not None else {}
        if metadata is not None:
            combined_meta.update(metadata)

        context = RevisionContext(backend=backend, extension=ext)
        with MeasureExecution("Bare revision"):
            # Create a bare revision first to get the API ID
            rev = gf.Revision(figure=target, metadata=combined_meta)
            target.revisions.create(rev)

            context.attach(rev)

        deferred = False
        if _GF_EXTENSION.cell is None:
            deferred = True
            get_extension().add_to_deferred(rev)

        with MeasureExecution("Image data"):
            rev.image_data, image_to_display = self._get_image_data(gf, backend, fig, rev, image_options)

        if image_to_display is not None and self.show_watermark:
            with SuppressDisplayTrap():
                if isinstance(image_to_display, gf.ImageData):
                    display(image_to_display.image)
                else:
                    display(image_to_display)

            if suppress_display is not None:
                suppress_display()

        if dataframes is not None:
            table_data = []
            for name, frame in dataframes.items():
                table_data.append(gf.TableData(name=name, dataframe=frame))

            rev.table_data = table_data

        if files is not None:
            rev.file_data = self._prepare_files(gf, files)

        if not deferred:
            with MeasureExecution("Annotators"):
                # Annotate the revision
                self.annotate(rev)

        with MeasureExecution("Final save"):
            rev.save(silent=True)

            # Calling .save() above will update internal properties based on the response from the server.
            # In our case, this will result in rev.figure becoming a shallow object with just the API ID. Here
            # we restore it from our cached copy, to avoid a separate API call.
            rev.figure = target

        _mark_as_published(fig)

        if self.clear and self.show_watermark:
            backend.close(fig)

        with SuppressDisplayTrap():
            self.widget_class(rev).show()

        return rev


def from_config_or_env(env_prefix, config_path):
    """\
    Decorator that binds function arguments in order of priority (most important first):
    1. args/kwargs
    2. environment variables
    3. vendor-specific secret manager
    4. config file
    5. function defaults

    :param env_prefix: prefix for environment variables. Variables are assumed to be named \
    `<prefix> + <name of function argument in all caps>`, e.g. if prefix is ``MYAPP`` and function argument \
    is called host_name, we'll look for an \
    environment variable named ``MYAPP_HOST_NAME``.
    :param config_path: path to the JSON config file. Function arguments will be looked up using their verbatim names.
    :return: decorated function

    """
    def decorator(func):
        @six.wraps(func)
        def wrapper(*args, **kwargs):
            # Read config file, if it exists
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    try:
                        config_file = json.load(f)
                    except Exception as e:
                        raise RuntimeError(f"Error parsing configuration file {config_path}") from e
            else:
                config_file = {}

            dbconfig = gofigr.databricks.get_config() or {}

            sig = inspect.signature(func)
            param_values = sig.bind_partial(*args, **kwargs).arguments
            for param_name in sig.parameters:
                env_name = f'{env_prefix}{param_name.upper()}'
                if param_name in param_values:
                    continue  # value supplied through args/kwargs: ignore env variables and the config file.
                elif env_name in os.environ:
                    param_values[param_name] = os.environ[env_name]
                elif param_name in dbconfig:
                    param_values[param_name] = dbconfig[param_name]
                elif param_name in config_file:
                    param_values[param_name] = config_file[param_name]

            return func(**param_values)

        return wrapper

    return decorator


def find_workspace_by_name(gf, search):
    """\
    Finds a workspace by name.

    :param gf: GoFigr client
    :param search: FindByName instance
    :return: a Workspace object

    """
    matches = [wx for wx in gf.workspaces if wx.name == search.name]
    if len(matches) == 0:
        if search.create:
            wx = gf.Workspace(name=search.name, description=search.description)
            wx.create()
            print(f"Created a new workspace: {wx.api_id}")
            return wx
        else:
            raise RuntimeError(f'Could not find workspace named "{search.name}"')
    elif len(matches) > 1:
        raise RuntimeError(f'Multiple (n={len(matches)}) workspaces match name "{search.name}". '
                           f'Please use an API ID instead.')
    else:
        return matches[0]


def proxy_callback(result):
    """Proxy callback"""
    if result is not None and hasattr(result, 'metadata'):
        get_extension().notebook_metadata = result.metadata

        if get_extension().is_ready:
            StartupWidget(get_extension()).show()


def _make_backend(backend):
    if isinstance(backend, GoFigrBackend):
        return backend
    else:
        return backend()


def _resolve_workspace(gf, workspace):
    if workspace is None:
        if gf.primary_workspace is not None:
            return gf.primary_workspace
        elif len(gf.workspaces) == 1:  # this will happen if we're using a scoped API token
            return gf.workspaces[0]
        else:
            raise ValueError("Please specify a workspace")
    else:
        return parse_model_instance(gf.Workspace, workspace, lambda search: find_workspace_by_name(gf, search))


# pylint: disable=too-many-arguments, too-many-locals
@from_config_or_env("GF_", os.path.join(os.environ['HOME'], '.gofigr'))
def configure(username=None,
              password=None,
              api_key=None,
              workspace=None,
              analysis=NotebookName(),
              url=API_URL,
              default_metadata=None, auto_publish=True,
              watermark=None, annotators=DEFAULT_ANNOTATORS,
              notebook_name=None, notebook_path=None,
              backends=DEFAULT_BACKENDS,
              widget_class=DetailedWidget,
              save_pickle=True,
              show_watermark=True):
    """\
    Configures the Jupyter plugin for use.

    :param username: GoFigr username (if used instead of API key)
    :param password: GoFigr password (if used instead of API key)
    :param api_key: API Key (if used instead of username and password)
    :param url: API URL
    :param workspace: one of: API ID (string), ApiId instance, or FindByName instance
    :param analysis: one of: API ID (string), ApiId instance, FindByName, or NotebookName instance
    :param default_metadata: dictionary of default metadata values to save for each revision
    :param auto_publish: if True, all figures will be published automatically without needing to call publish()
    :param watermark: custom watermark instance (e.g. DefaultWatermark with custom arguments)
    :param annotators: list of annotators to use. Default: DEFAULT_ANNOTATORS
    :param notebook_name: name of the notebook (if you don't want it to be inferred automatically)
    :param notebook_path: path to the notebook (if you don't want it to be inferred automatically)
    :param backends: backends to use (e.g. MatplotlibBackend, PlotlyBackend)
    :param widget_class: Widget type to show, e.g. DetailedWidget or CompactWidget. It will appear below the
        published figure
    :param save_pickle: if True, will save the figure in pickle format in addition to any of the image formats
    :param show_watermark: True to show watermarked figures instead of original.
        False to always display the unmodified figure. Default True.
    :return: None

    """
    extension = _GF_EXTENSION

    if isinstance(auto_publish, str):
        auto_publish = auto_publish.lower() == "true"  # in case it's coming from an environment variable

    with MeasureExecution("Login"):
        gf = GoFigr(username=username, password=password, url=url, api_key=api_key)

    workspace = _resolve_workspace(gf, workspace)

    with MeasureExecution("Fetch workspace"):
        try:
            workspace.fetch()
        except UnauthorizedError as e:
            raise UnauthorizedError(f"Permission denied for workspace {workspace.api_id}. "
                                    f"Are you using a restricted API key?") from e

    if analysis is None:
        raise ValueError("Please specify an analysis")
    elif isinstance(analysis, NotebookName) or str(analysis) == "NotebookName":  # str in case it's from config/env
        analysis = NotebookName()
    else:
        with MeasureExecution("Find analysis"):
            analysis = parse_model_instance(gf.Analysis, analysis,
                                            lambda search: workspace.get_analysis(name=search.name,
                                                                                  description=search.description,
                                                                                  create=search.create))

        with MeasureExecution("Fetch analysis"):
            analysis.fetch()

    if default_metadata is None:
        default_metadata = {}

    if notebook_path is not None:
        default_metadata['notebook_path'] = notebook_path

    if notebook_name is not None:
        default_metadata['notebook_name'] = notebook_name

    publisher = Publisher(gf,
                          default_metadata=default_metadata,
                          watermark=watermark,
                          annotators=[make_annotator(extension) for make_annotator in annotators],
                          backends=[_make_backend(bck) for bck in backends],
                          widget_class=widget_class,
                          save_pickle=save_pickle,
                          show_watermark=show_watermark)
    extension.gf = gf
    extension.analysis = analysis
    extension.workspace = workspace
    extension.publisher = publisher
    extension.auto_publish = auto_publish
    extension.loader_shown = False
    extension.configured = True

    if get_extension().is_ready:
        StartupWidget(get_extension()).show()


@require_configured
def publish(fig=None, backend=None, **kwargs):
    """\
    Publishes a figure. See :func:`gofigr.jupyter.Publisher.publish` for a list of arguments. If figure and backend
    are both None, will publish default figures across all available backends.

    :param fig: figure to publish
    :param backend: backend to use
    :param kwargs:
    :return:

    """
    ext = get_extension()

    if fig is None and backend is None:
        # If no figure and no backend supplied, publish default figures across all available backends
        for available_backend in ext.publisher.backends:
            fig = available_backend.get_default_figure(silent=True)
            if fig is not None:
                ext.publisher.publish(fig=fig, backend=available_backend, **kwargs)
    else:
        ext.publisher.publish(fig=fig, backend=backend, **kwargs)


@require_configured
def get_gofigr():
    """Gets the active GoFigr object."""
    return get_extension().gf


@require_configured
def load_pickled_figure(api_id):
    """\
    Unpickles a GoFigr revision and returns it as a backend-specific Python object, e.g. a plt.Figure if
    the figure was generated with matplotlib. Throws a RuntimeException if the figure is not found or does
    not have pickle data.

    :param api_id: API ID of the revision
    :return: backend-dependent figure object, e.g. plt.Figure().

    """
    gf = get_gofigr()
    rev = gf.Revision(api_id=api_id).fetch(fetch_data=False)
    for data in rev.image_data:
        if data.format == "pickle":
            data.fetch()

            fig = pickle.load(io.BytesIO(data.data))
            return _mark_as_published(fig)

    raise RuntimeError("This revision doesn't have pickle data.")


@require_configured
def download_file(api_id, file_name, path):
    """\
    Downloads a file and saves it.

    :param api_id: API ID of the revision containing the file
    :param file_name: name of the file to download
    :param path: where to save the file (either existing directory or full path with the file name)
    :return: number of bytes written

    """
    if os.path.exists(path) and os.path.isdir(path):
        path = os.path.join(path, file_name)

    gf = get_gofigr()
    rev = gf.Revision(api_id=api_id).fetch(fetch_data=False)
    for data in rev.file_data:
        if data.name == file_name:
            data.fetch()
            data.write(path)
            return len(data.data)

    raise RuntimeError(f"Could not find file \"{file_name}\" in revision {api_id}.")


@require_configured
def download_all(api_id, path):
    """\
    Downloads all files attached to a revision

    :param api_id: API ID of the revision containing the files
    :param path: directory where to save the files
    :return: number of bytes written

    """
    if not os.path.exists(path) or not os.path.isdir(path):
        raise RuntimeError(f"{path} does not exist or is not a directory")

    gf = get_gofigr()
    rev = gf.Revision(api_id=api_id).fetch(fetch_data=False)
    num_bytes = 0
    for data in rev.file_data:
        data.fetch()
        data.write(os.path.join(path, data.name))
        num_bytes += len(data.data)

    return num_bytes
