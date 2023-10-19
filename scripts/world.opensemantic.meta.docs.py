from pathlib import Path

from reusable import WorldCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Docs - Core",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.meta.docs",
    # Package ID - usually the same as repo
    id="world.opensemantic.meta.docs.core",
    # Package subdirectory - usually resembling parts of the package name
    subdir="core",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("Provides core documentation of OpenSemanticWorld / -Lab"),
    # Specify the package version - use semantic versioning
    version="0.6.2",
    # Author(s)
    author=["Simon Stier", "Lukas Gold", "Andeas Räder"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Item:OSW70b4d6464c1d44a887eb86e3b39b8751",  # StructedDataWorkshop
        "Item:OSWf1df064239044b8fa3c968339fb93344",  # JsonTutorial
        "Item:OSWf4a9514baed04859a4c6c374a7312f10",  # JsonSchemaTutorial
        "Item:OSW911488771ea449a6a34051f8213d7f2f",  # JsonLdTutorial
        "Item:OSWee501c0fa6a9407d99c058b5ff9d55b4",  # JsonApplicationTutorial
        "Item:OSW6df03625b42e4b44bd9f2dfa77387887",  # HandlebarsTemplates
        "Item:OSW18201c9a18f64574a12d97efdeb2f953",  # SchemaTemplateTutorial
        "Item:OSW7d3292e5104f45b1be4fc23901fae4fa",  # TabularData
        "Item:OSW52c2c5a6bbc84fcb8eab0fa69857e7dc",  # ArticleTutorial
        "Item:OSW7113f5cf921a4c82ad1872afeff9d01d",  # TranscendWikitext
        "Item:OSWab674d663a5b472f838d8e1eb43e6784",  # OswSchema
        "Item:OSW659a81662ff44af1b2b6febeee7c3a25",  # OswPythonPackage
        # "Item:OSW92619b0700984fe7913e5fbbd7f194dc", # OswSpecialEditors
        "Item:OSWc596ce27af054764ae9716748d01555e",  # OswOntologyImport
        "Item:OSWdb485a954a88465287b341d2897a84d6",  # OswIntroduction
    ],
)
# Provide the information needed (only) to create the page package
package_creation_config = WorldCreat(
    # Specify the path to the working directory - where the package is stored on disk
    working_dir=Path(__file__).parents[1]
    / "packages"
    / package_meta_data.repo,
)
# Create the page package
package_meta_data.create(
    creation_config=package_creation_config,
)
