"""Tests for sidechainnet.utils.parse.py."""

from sidechainnet.utils.download import ASTRAL_ID_MAPPING
import sidechainnet.utils.parse as parse


# Tests for ASTRAL IDs
def test_astral_ids_with_insertion_codes():
    pnid = "1JQG_d1jqga2"
    pdbid, astral_id = pnid.split("_")
    chain = parse.get_chain_from_astral_id(astral_id.replace("-", "_"), ASTRAL_ID_MAPPING)
    # Currently ProDy does not parse the range correctly, but ProDy issue #1197 may fix it
    assert len(chain.ca) > 2
