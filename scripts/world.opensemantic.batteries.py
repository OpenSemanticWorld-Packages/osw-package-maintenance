from pathlib import Path

from reusable import WorldCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Batteries",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.batteries",
    # Package ID - usually the same as repo
    id="world.opensemantic.batteries",
    # Package subdirectory - usually resembling parts of the package name
    subdir="batteries",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=(
        "Provides battery specific items like ElectrochemicalTest, " "BatteryCell, etc."
    ),
    # Specify the package version - use semantic versioning
    version="0.1.0",
    # Author(s)
    author=["Simon Stier", "Lukas Gold"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Category:OSWe427aafafbac4262955b9f690a83405d",  # Tool
        "Category:OSWf0fe562f422d49c6877490b3dfee2f3f",  # Device
        "Category:OSWe0572f2791844010962886b892970b4d",  # Controlled Environment
        "Category:OSWb3b9ec5cb50d401c9b996ce3009b5c54",  # Environmental Test Chamber
        "Category:OSW43b7a7cf767c4c529ac260b117d19773",  # Climate Test Chamber
        "Category:OSW4ebd1194039943018ace13cd4c94774a",  # Temperature Test Chamber
        "Category:OSW5e3a5c9228ad4aec98830900e247ff39",  # Memmert
        # Peltier CooledIncubator
        "Category:OSWa36c243bd489400fb25857c1d9626383",  # Memmert IPP250plus
        "Category:OSW8355078074764a82bfddf43a25428a45",  # Vötsch Temperature Test
        # Chamber
        "Category:OSWaf33780e29a84867a6791555d23e8d5e",  # Vötsch VT 4021-S
        "Category:OSWf6f9f6c1c8f943909ffe681bca67252a",  # Glovebox
        "Category:OSW1849e7e9b69e445da44f50093a1d585b",  # MBRAUN Glovebox
        "Category:OSW85ab3eb019fb434aa7075ae6c008ede2",  # MB200MOD
        "Category:OSW69729530f3ca4addaf8dd95ea3781607",  # Electrochemical Testing
        # Device
        "Category:OSWef181c1daf2343fd8c132c39e7d748bd",  # Maccor Battery Tester
        "Category:OSWd5b87e52a61349dbb6077bf2447a7bf4",  # Maccor Series 4000
        "Category:OSWe5aa96bffb1c4d95be7fbd46142ad203",  # Process
        "Category:OSWfa0d5710bc0f45819b61b65fc4fd9656",  # Strict Participants Process
        "Category:OSW1a271f289649413488e2841580e43a45",  # Administrative Process
        "Category:OSW3886740859ae459588fee73d3bb3c83e",  # Risk Assessment Process
        "Category:OSW0e7fab2262fb4427ad0fa454bc868a0d",  # ElnEntry
        "Category:OSW47c67760dd164c82b570f58c8269b373",  # Post Mortem Experiment
        "Category:OSWafda1f2328804e3a89bf90f8af9c5527",  # Battery Cell Opening
        "Category:OSW6f39d77241e24a33ab6d036dfac03ace",  # Electrochemical Test
        "Category:OSWe21775c8dd604739885dfc24c32cc548",  # Procedure
        "Category:OSWdda41d4a4ec0421babe0295c6edcb5df",  # Electrochemical Test
        # Procedure
        "Category:OSWdda41d4a4ec0421babe0295c6edcb5df",  # Battery Test Procedure
        "Category:OSWbdb8b449342e4090b44b4f80c5ae9d92",  # Maccor Test Procedure
        "Category:OSW18f3251c2562407ea7bd7b19791b76f0",  # Bio-Logic Test Procedure
        "Category:OSW31ca9a739cb24079b36824045c0832aa",  # Material
        "Category:OSW88894b63a51d46b08b5b4b05a6b1b3c3",  # Sample
        "Category:OSW0c3ab986534b44cf806a6f111094d61e",  # Battery Cell
        "Category:OSW9cf86699d6ba4b8c841a8e77e17a63ed",  # Material Type
        "Category:OSW0583b134c618484c9911a3dff145c7eb",  # Sample Type
        "Category:OSWb85e46ebb9ca4c83aac27e2c01dde369",  # Battery Cell Type
        "Category:TermNew" "Category:OSWa211cf52e86e47929768a769235f7144",  # Format
        "Category:OSWf04e73d3c3cb4e4ea7033066e472e9ff",  # Battery Cell Format
        "Item:OSWd208bb6b47e1481c962cdc67975a2004",  # Coin Cell
        "Item:OSWd208bb6b47e1481c962cdc67975a2004",  # Cylindrical Cell
        "Item:OSW8d3a70c2a0c6486d81867be27dcff6db",  # Pouch Cell
        "Item:OSW5c944ba0f91e48878ff7df8525751747",  # Prismatic Cell
    ],
)
# Provide the information needed (only) to create the page package
package_creation_config = WorldCreat(
    # Specify the path to the working directory - where the package is stored on disk
    working_dir=Path(__file__).parents[1]
    / "packages"
    / package_meta_data.repo,
)

if __name__ == "__main__":
    # Create the page package
    package_meta_data.create(
        creation_config=package_creation_config,
    )
