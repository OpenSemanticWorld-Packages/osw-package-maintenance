"""Migrate OpcUaServer instance data after world.opensemantic.lab schema update.

Source: world.opensemantic.lab v0.7.0 (commit c47c2a1, 2026-04-29)
Target: world.opensemantic.lab v0.9.0 (commit 791f06b, 2026-05-09)

Changes to OpcUaServer (Category:OSW89fda9fed80b41b1ad4c0c011e645600):
  - `sampling_interval_in_milliseconds` (integer) renamed to `sampling_interval`
    (Time characteristic object with value + unit)
  - `refresh_interval_in_milliseconds` (integer) renamed to `refresh_interval`
    (Time characteristic object with value + unit)
  - Added `url` field (no migration needed, empty by default)
  - Added `subchannels` field (no migration needed)

Prerequisite: run base migration first (migrate_world.opensemantic.base_0.42.6-405159c_to_0.42.8-4295326.py)
to add osw_id fields.

Applies to all instances of OpcUaServer and its subclasses (EvacuationUnit, etc.).

Usage:
    # Dry-run (default)
    python scripts/migrations/migrate_world.opensemantic.lab_0.7.0-c47c2a1_to_0.9.0-791f06b.py

    # Execute
    python scripts/migrations/migrate_world.opensemantic.lab_0.7.0-c47c2a1_to_0.9.0-791f06b.py --execute

    # Target a specific wiki
    python scripts/migrations/migrate_world.opensemantic.lab_0.7.0-c47c2a1_to_0.9.0-791f06b.py -d test.terravac.cloud --cred-file path/to/accounts.pwd.yaml
"""

import sys

from migration_base import run_migration
from osw.wtsite import WtPage

# Millisecond unit Item ID (prefix unit of Second in world.opensemantic.quantities)
MILLISECOND_UNIT = (
    "Item:OSW85302b21cf045998b80f38c9fdb88f84"
    "#OSW84d4f530814e5251b06e73ee0184e32b"
)

DEFAULT_CATEGORIES = [
    "Category:OSW89fda9fed80b41b1ad4c0c011e645600",  # OpcUaServer
]

DEFAULT_COMMENT = (
    "Migrate OpcUaServer data_channels: convert interval fields "
    "to Time characteristic (lab v0.7.0 -> v0.9.0)"
)


def migrate_page(page: WtPage, page_title: str) -> bool:
    """Migrate OpcUaServer-level channel fields: convert interval fields to Time objects.

    Returns True if the page was modified.
    """
    jd = page.get_slot_content("jsondata")
    if not isinstance(jd, dict):
        print(f"  skipped (jsondata is not a dict)")
        return False

    channels = jd.get("data_channels")
    if not isinstance(channels, list):
        print(f"  skipped (no data_channels array)")
        return False

    changed = False
    for i, channel in enumerate(channels):
        if not isinstance(channel, dict):
            continue
        prefix = f"  channel[{i}] ({channel.get('name', channel.get('node_id', '?'))}): "

        for old_key, new_key in [
            ("sampling_interval_in_milliseconds", "sampling_interval"),
            ("refresh_interval_in_milliseconds", "refresh_interval"),
        ]:
            if old_key in channel:
                old_value = channel.pop(old_key)
                if old_value is not None:
                    channel[new_key] = {
                        "value": old_value,
                        "unit": MILLISECOND_UNIT,
                    }
                    print(
                        f"{prefix}{old_key}={old_value} "
                        f"-> {new_key}={{value: {old_value}, unit: ms}}"
                    )
                else:
                    print(f"{prefix}{old_key}=None -> removed")
                changed = True

    if changed:
        page.set_slot_content("jsondata", jd)

    return changed


if __name__ == "__main__":
    sys.exit(run_migration(
        description=__doc__.split("\n")[0],
        default_categories=DEFAULT_CATEGORIES,
        default_comment=DEFAULT_COMMENT,
        migrate_page=migrate_page,
    ))
