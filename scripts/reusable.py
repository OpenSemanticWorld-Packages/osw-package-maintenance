from pathlib import Path

import osw.model.page_package as package


class WorldMeta(package.PagePackageMetaData):
    # name: is required but not provided here -> needs to be set in each script
    # repo: is required but not provided here -> needs to be set in each script
    # id: is required but not provided here -> needs to be set in each script
    # subdir: is required but not provided here -> needs to be set in each script
    # branch: is required but not provided here -> needs to be set in each script
    repo_org = "OpenSemanticWorld-Packages"
    # description: is required but not provided here -> needs to be set in each script
    language = "en"
    # version: is required but not provided here -> needs to be set in each script
    # authors: is required but not provided here -> needs to be set in each script
    publisher = "OpenSemanticWorld"
    # page_titles: is required but not provided here -> needs to be set in each script


class WorldCreat(package.PagePackageCreationConfig):
    domain = ("wiki-dev.open-semantic-lab.org",)
    credentials_file_path = Path(__file__).parent / "accounts.pwd.yaml"
    # working_dir: is required but not provided here -> needs to be set in each script


class OslMeta(package.PagePackageMetaData):
    repo_org = "OpenSemanticLab"
    language = "en"
    publisher = "OpenSemanticLab"


class OslCreat(package.PagePackageCreationConfig):
    domain = ("wiki-dev.open-semantic-lab.org",)
    credentials_file_path = Path(__file__).parent / "accounts.pwd.yaml"
