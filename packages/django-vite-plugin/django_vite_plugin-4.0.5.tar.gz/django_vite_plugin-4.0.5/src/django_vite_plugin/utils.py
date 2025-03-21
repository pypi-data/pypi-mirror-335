from typing import Dict
from django.conf import settings
from django.contrib.staticfiles import finders
from urllib.parse import urljoin
from .config_helper import get_config
import json
import sys

# Length of the root directory
ROOT_DIR_LEN = len(str(getattr(settings, "BASE_DIR")))

# Cache for previously searched files map
FOUND_FILES_CACHE = {}

CONFIG = get_config()

# Make sure 'BUILD_URL_PREFIX' finish with a '/'
if CONFIG['BUILD_URL_PREFIX'][-1] != "/":
    CONFIG['BUILD_URL_PREFIX'] += "/"

if CONFIG['DEV_MODE'] is False and 'JS_ATTRS_BUILD' in CONFIG:
    CONFIG['JS_ATTRS'] = CONFIG['JS_ATTRS_BUILD']

VITE_MANIFEST  = {}
DEV_SERVER = None

if not CONFIG['DEV_MODE']:
    manifest_path = CONFIG['MANIFEST']
    try:
        with open(manifest_path, "r") as manifest_file:
            VITE_MANIFEST = json.load(manifest_file)
    except FileNotFoundError:
        sys.stderr.write(f"Cannot read Vite manifest file at {manifest_path}\n")
    except Exception as error:
        raise RuntimeError(f"Cannot read Vite manifest file at {manifest_path}: {error}")


def make_attrs(attrs: Dict[str, any]):
    """
    Compile attributes to a string
    if attr is True then just add the attribute
    """
    attr_str = ''
    for key, val in attrs.items():
        attr_str += key

        if val is False:
            attr_str += '="false"'
        elif val is not True:
            attr_str += f'="{val}"'
        attr_str += ' '
    return attr_str[0:-1]



# Compile the default css attributes beforehand
DEFAULT_CSS_ATTRS = make_attrs(CONFIG['CSS_ATTRS'])


def get_from_manifest(path: str, attrs: Dict[str, str]) -> str:
    if path not in VITE_MANIFEST:
        raise RuntimeError(
            f"Cannot find {path} in Vite manifest "
        )
    
    manifest_entry = VITE_MANIFEST[path]
    assets = _get_css_files(manifest_entry, {
        # The css files of a js 'import' should get the default attributes
        'css': DEFAULT_CSS_ATTRS
    })
    assets += get_html(
        urljoin(CONFIG['BUILD_URL_PREFIX'], manifest_entry["file"]),
        attrs
    )

    return assets



def _get_css_files(
    manifest_entry: Dict[str, str],
    attrs: Dict[str, str],
    already_processed = None
) -> str:
    if already_processed is None:
        already_processed = []
    html = ''

    if 'imports' in manifest_entry:
        for import_path in manifest_entry['imports']:
            html += _get_css_files(
                VITE_MANIFEST[import_path],
                attrs,
                already_processed
            )

    if 'css' in manifest_entry:
        for css_path in manifest_entry['css']:
            if css_path not in already_processed:
                html += get_html(
                    urljoin(CONFIG['BUILD_URL_PREFIX'], css_path),
                    attrs
                )
            already_processed.append(css_path)

    return html



def get_html(url: str, attrs: Dict[str, str]) -> str:
    if url.endswith('.css'):
        return f'<link {attrs["css"]} href="{url}" />'
    else:
        return f'<script {attrs["js"]} src="{url}"></script>'
    

def get_html_dev(url: str, attrs: Dict[str, str]) -> str:
    global DEV_SERVER
    if DEV_SERVER is None:
        try:
            with open(CONFIG['HOT_FILE'], 'r') as hotfile:
                DEV_SERVER = hotfile.read()
        except:
            raise Exception("Vite dev server is not started!")
    if url.endswith(('.css', '.scss', '.sass', '.less')):
        return f'<link {attrs["css"]} href="{DEV_SERVER}/{url}" />'
    elif url == 'react':
        return f"""
        <script type="module">
        import RefreshRuntime from "{DEV_SERVER}/@react-refresh"
        RefreshRuntime.injectIntoGlobalHook(window)
        window.$RefreshReg$ = () => {{}}
        window.$RefreshSig$ = () => (type) => type
        window.__vite_plugin_react_preamble_installed__ = true
        </script>
        """
    else:
        return f'<script {attrs["js"]} src="{DEV_SERVER}/{url}"></script>'
    


def find_asset(arg: str) -> str:
    """
    If `STATIC_LOOKUP` is enabled then find the asset
    using djang's built-in static finder

    Cache the found files for later use
    """
    

    if arg in FOUND_FILES_CACHE:
        return FOUND_FILES_CACHE[arg] 
    
    if not CONFIG['STATIC_LOOKUP']:
        return arg
    

    found = finders.find(arg, False)

    if found is None:
        final = arg.strip('/\\')
    else:
        final = found[ROOT_DIR_LEN:].strip('/\\').replace('\\', '/')

    FOUND_FILES_CACHE[arg] = final

    return final
