from pathlib import Path
from typing import Optional

from osw.controller.page_package import PagePackageController as Package
from pydantic import FilePath


DEFAULT_CREDENTIALS_FILE_PATH = Path(__file__).parent / "accounts.pwd.yaml"


class WorldMeta(Package):
    """Metadata for the world.opensemantic page packages"""

    # name: is required but not provided here -> needs to be set in each script
    # repo: is required but not provided here -> needs to be set in each script
    # id: is required but not provided here -> needs to be set in each script
    # subdir: is required but not provided here -> needs to be set in each script
    # branch: is required but not provided here -> needs to be set in each script
    repo_org = "OpenSemanticWorld-Packages"
    # description: is required but not provided here -> needs to be set in each script
    language = "en"
    # version: is required but not provided here -> needs to be set in each script
    # author: is required but not provided here -> needs to be set in each script
    publisher = "OpenSemanticWorld"
    # page_titles: is required but not provided here -> needs to be set in each script


class WorldCreat(Package.CreationConfig):
    """Creation config for the world.opensemantic page packages"""

    domain = "wiki-dev.open-semantic-lab.org"
    credentials_file_path: Optional[FilePath] = DEFAULT_CREDENTIALS_FILE_PATH
    # working_dir: is required but not provided here -> needs to be set in each script


class OslMeta(Package):
    """Metadata for the org.open-semantic-lab page packages"""

    repo_org = "OpenSemanticLab"
    language = "en"
    publisher = "OpenSemanticLab"


class OslCreat(Package.CreationConfig):
    """Creation config for the org.open-semantic-lab page packages"""

    domain = "wiki-dev.open-semantic-lab.org"
    credentials_file_path: Optional[FilePath] = DEFAULT_CREDENTIALS_FILE_PATH
    skip_slot_suffix_for_main = True


class BigMapCreat(Package.CreationConfig):
    """Creation config for the org.open-semantic-lab page packages"""

    domain = "osl-sandbox.big-map.eu"
    credentials_file_path: Optional[FilePath] = DEFAULT_CREDENTIALS_FILE_PATH
    skip_slot_suffix_for_main = True
