"""Migrate DataTool instance data after world.opensemantic.base schema update.

Source: world.opensemantic.base v0.42.6 (commit 405159c, 2026-04-22)
Target: world.opensemantic.base v0.42.8 (commit 4295326, 2026-05-09)

Changes to DataTool (Category:OSWda27e2fff10848ebb728ffb69c49a16d):
  - data_channels items now require `osw_id` (computed from page title + channel uuid)
  - The old `type` field (autocomplete) in channel items is deprecated and removed

Applies to all instances of DataTool and its subclasses (OpcUaServer, etc.).

Usage:
    # Dry-run (default)
    python scripts/migrations/migrate_world.opensemantic.base_0.42.6-405159c_to_0.42.8-4295326.py

    # Execute
    python scripts/migrations/migrate_world.opensemantic.base_0.42.6-405159c_to_0.42.8-4295326.py --execute

    # Target a specific wiki
    python scripts/migrations/migrate_world.opensemantic.base_0.42.6-405159c_to_0.42.8-4295326.py -d test.terravac.cloud --cred-file path/to/accounts.pwd.yaml
"""

import sys

from migration_base import run_migration
from osw.wtsite import WtPage

DEFAULT_CATEGORIES = [
    "Category:OSWda27e2fff10848ebb728ffb69c49a16d",  # DataTool
]

DEFAULT_COMMENT = (
    "Migrate data_channels: add osw_id, remove deprecated type "
    "(base v0.42.6 -> v0.42.8)"
)


def compute_osw_id(page_title: str, channel_uuid: str) -> str:
    """Compute the osw_id for a data channel from page title and channel uuid."""
    uuid_no_dashes = channel_uuid.replace("-", "")
    return f"{page_title}#OSW{uuid_no_dashes}"


def migrate_page(page: WtPage, page_title: str) -> bool:
    """Migrate DataTool-level channel fields: add osw_id, remove deprecated type.

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
        prefix = f"  channel[{i}] ({channel.get('name', '?')}): "

        # Add osw_id if missing
        uuid_val = channel.get("uuid")
        if uuid_val and "osw_id" not in channel:
            channel["osw_id"] = compute_osw_id(page_title, uuid_val)
            print(f"{prefix}added osw_id={channel['osw_id']}")
            changed = True

        # Remove deprecated `type` field from channel items.
        # Only remove if it is the old autocomplete value (a Category: string),
        # not a list (which would be the schema type default).
        ch_type = channel.get("type")
        if isinstance(ch_type, str) and ch_type.startswith("Category:"):
            del channel["type"]
            print(f"{prefix}removed deprecated channel type={ch_type}")
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
