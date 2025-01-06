# osw-package-maintenance

Python scripts to build OSW page packages, common page package repositories as submodules

To add a package, run

```bash
git submodule add <package_repo> packages/<package_name>
```

e. g.

```bash
git submodule add https://github.com/OpenSemanticWorld-Packages/world.opensemantic.core packages/world.opensemantic.core
```

## Page packages

```mermaid
classDiagram
    %% Define class and link here
    %% Stick to alphabetical order
    class base
    link base "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.base" "world.opensemantic.base"
    class batteries
    link batteries "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.batteries" "world.opensemantic.batteries"
    class core {Technical core requirements}
    link core "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.core" "world.opensemantic.core"
    class demo
    link demo "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.demo" "world.opensemantic.demo"
    class demo_lab_virtual
    link demo_lab_virtual "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.demo.lab.virtual" "world.opensemantic.demo.lab.virtual"
    class lab
    link lab "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.lab" "world.opensemantic.lab"
    class lab_virtual
    link lab_virtual "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.lab.virtual" "world.opensemantic.lab.virtual"
    class meta_docs
    link meta_docs "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.meta.docs" "world.opensemantic.meta.docs"
    class meta_legal
    link meta_legal "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.meta.legal" "world.opensemantic.meta.legal"
    class ontology
    link ontology "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.ontology" "world.opensemantic.ontology"

    class core_mediawiki
    link core_mediawiki "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.core.mediawiki" "world.opensemantic.core.mediawiki"

    class characteristics_basic
    link characteristics_basic "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.characteristics.basic" "world.opensemantic.characteristics.basic"
    class quantities
    link quantities "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.quantities" "world.opensemantic.quantities"
    class characteristics_quantitative
    link characteristics_quantitative "https://github.com/OpenSemanticWorld-Packages/world.opensemantic.characteristics.quantitative" "world.opensemantic.characteristics.quantitative"


    %% Define dependencies here
    %% Inheritance is used to model the "requiredPackage" relation
    %% Order the inheriting packages alphabetically
    core        <|-- base
    core        <|-- core_mediawiki
    base        <|-- batteries
    lab         <|-- batteries
    lab         <|-- demo
    lab_virtual <|-- demo_lab_virtual
    base        <|-- lab
    lab         <|-- lab_virtual
    base        <|-- meta_docs
    core        <|-- ontology
    core        <|-- characteristics_basic
    characteristics_basic        <|-- quantities
    quantities  <|-- characteristics_quantitative
```

## Contribute

To contribute to this repository, please fork it and create a pull request.

When adding a new package, please add it and its dependencies (requiredPackages) to the mermaid dependency graph.
