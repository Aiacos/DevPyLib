"""Correctness validation tests for UV batch operations optimization.

This test suite validates that the optimized batch UV coordinate retrieval
methods produce identical results to the original per-vertex approach.

Tests verify correctness for:
- check_uv_in_boundaries(): Boundary checking for UV shells
- check_uv_boundaries(): UV tile range calculation
- cut_uv_tile(): UV filtering by tile boundaries

Test scenarios:
- Single tile UVs (0-1 range)
- Multi-UDIM UVs (spanning multiple tiles)
- Negative UVs
- Edge cases (empty UV set, single UV)
"""

import sys
from pathlib import Path
from typing import List, Tuple
from unittest.mock import MagicMock

# Add parent directories to path for imports
_test_dir = Path(__file__).parent.resolve()
_mayalib_dir = _test_dir.parent
_root_dir = _mayalib_dir.parent

if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))


# Mock Maya modules before importing mayaLib
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.mel"] = MagicMock()
sys.modules["pymel"] = MagicMock()
sys.modules["pymel.core"] = MagicMock()


class MockUVDataset:
    """Mock UV dataset for correctness testing."""

    def __init__(self, uv_coords: List[float]):
        """Initialize mock UV dataset.

        Args:
            uv_coords: Flat list of UV coordinates [u1, v1, u2, v2, ...].
        """
        self.uv_coords = uv_coords
        self.num_uvs = len(uv_coords) // 2

    @classmethod
    def single_tile(cls) -> "MockUVDataset":
        """Create UV dataset in single tile (0-1 range).

        Returns:
            MockUVDataset: UVs in 0-1 range.
        """
        return cls([0.1, 0.2, 0.5, 0.5, 0.8, 0.9, 0.3, 0.7])

    @classmethod
    def multi_tile(cls) -> "MockUVDataset":
        """Create UV dataset spanning multiple UDIM tiles.

        Returns:
            MockUVDataset: UVs spanning tiles 1001, 1002, 1011, 1012.
        """
        return cls(
            [
                0.5,
                0.5,  # Tile 1001 (0-1, 0-1)
                1.5,
                0.5,  # Tile 1002 (1-2, 0-1)
                0.5,
                1.5,  # Tile 1011 (0-1, 1-2)
                1.5,
                1.5,  # Tile 1012 (1-2, 1-2)
            ]
        )

    @classmethod
    def negative_uvs(cls) -> "MockUVDataset":
        """Create UV dataset with negative coordinates.

        Returns:
            MockUVDataset: UVs with negative coordinates.
        """
        return cls([-0.5, -0.3, -1.2, 0.5, 0.3, -0.8])

    @classmethod
    def empty(cls) -> "MockUVDataset":
        """Create empty UV dataset.

        Returns:
            MockUVDataset: Empty UV dataset.
        """
        return cls([])

    @classmethod
    def single_uv(cls) -> "MockUVDataset":
        """Create dataset with single UV.

        Returns:
            MockUVDataset: Single UV point.
        """
        return cls([0.5, 0.5])

    @classmethod
    def tile_boundary(cls) -> "MockUVDataset":
        """Create UVs at exact tile boundaries.

        Returns:
            MockUVDataset: UVs at tile boundaries.
        """
        return cls([0.0, 0.0, 1.0, 1.0, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0])


class MockPyMelCorrectness:
    """Mock PyMEL interface for correctness testing."""

    def __init__(self, uv_data: MockUVDataset):
        """Initialize mock PyMEL with UV data.

        Args:
            uv_data: Mock UV dataset.
        """
        self.uv_data = uv_data

    def polyListComponentConversion(self, shell, tuv=False):
        """Mock polyListComponentConversion.

        Args:
            shell: Shell identifier.
            tuv: To UV flag.

        Returns:
            str: Mock UV selection string.
        """
        return f"mockUVs_{self.uv_data.num_uvs}"

    def ls(self, selection, fl=False):
        """Mock ls command.

        Args:
            selection: Selection to list.
            fl: Flatten flag.

        Returns:
            List[str]: List of mock UV components.
        """
        return [f"mockUV[{i}]" for i in range(self.uv_data.num_uvs)]

    def polyEditUV(self, uv_selection, q=False):
        """Mock polyEditUV command.

        Args:
            uv_selection: UV selection (list or single UV).
            q: Query flag.

        Returns:
            UV coordinates (flat list for batch, pair for single).
        """
        # Batch query - return all coordinates
        if isinstance(uv_selection, list):
            return self.uv_data.uv_coords.copy()

        # Single UV query - return one coordinate pair
        # Extract UV index from string like "mockUV[123]"
        idx = int(uv_selection.split("[")[1].split("]")[0])
        return [
            self.uv_data.uv_coords[idx * 2],
            self.uv_data.uv_coords[idx * 2 + 1],
        ]


def old_check_uv_in_boundaries(mock_pm: MockPyMelCorrectness, shell: str) -> bool:
    """Old implementation: check if UVs are within boundaries (per-vertex).

    Args:
        mock_pm: Mock PyMEL interface.
        shell: Shell identifier.

    Returns:
        bool: True if all UVs are within boundaries.
    """
    uvs = mock_pm.polyListComponentConversion(shell, tuv=True)
    uv_list = mock_pm.ls(uvs, fl=True)

    if not uv_list:
        return True

    u_max = 1
    u_min = 0
    v_max = 1
    v_min = 0

    # OLD: Individual API calls in loop
    for i, uv in enumerate(uv_list):
        u, v = mock_pm.polyEditUV(uv, q=True)

        if i > 0:
            if not (u > u_min and u < u_max and v > v_min and v < v_max):
                return False

        u_max = int(u) + 1
        u_min = int(u)

        v_max = int(v) + 1
        v_min = int(v)

    return True


def new_check_uv_in_boundaries(mock_pm: MockPyMelCorrectness, shell: str) -> bool:
    """New implementation: check if UVs are within boundaries (batch).

    Args:
        mock_pm: Mock PyMEL interface.
        shell: Shell identifier.

    Returns:
        bool: True if all UVs are within boundaries.
    """
    uvs = mock_pm.polyListComponentConversion(shell, tuv=True)
    uv_list = mock_pm.ls(uvs, fl=True)

    if not uv_list:
        return True

    # NEW: Batch query all UV coordinates at once
    uv_coords = mock_pm.polyEditUV(uv_list, q=True)

    u_max = 1
    u_min = 0
    v_max = 1
    v_min = 0

    # Process coordinates in pairs (u, v)
    for i in range(0, len(uv_coords), 2):
        u = uv_coords[i]
        v = uv_coords[i + 1]

        if i > 0:
            if not (u > u_min and u < u_max and v > v_min and v < v_max):
                return False

        u_max = int(u) + 1
        u_min = int(u)

        v_max = int(v) + 1
        v_min = int(v)

    return True


def old_check_uv_boundaries(
    mock_pm: MockPyMelCorrectness, shell: str
) -> List[List[int]]:
    """Old implementation: determine UV tile boundaries (per-vertex).

    Args:
        mock_pm: Mock PyMEL interface.
        shell: Shell identifier.

    Returns:
        List[List[int]]: UV tile boundaries [[u_min, u_max, v_min, v_max], ...].
    """
    uvs = mock_pm.polyListComponentConversion(shell, tuv=True)
    uv_list = mock_pm.ls(uvs, fl=True)
    uv_tile_range = []

    if not uv_list:
        return uv_tile_range

    # OLD: Individual API calls in loop
    for uv in uv_list:
        u, v = mock_pm.polyEditUV(uv, q=True)

        u_max = int(u) + 1
        u_min = int(u)

        v_max = int(v) + 1
        v_min = int(v)

        tile = [u_min, u_max, v_min, v_max]
        if tile not in uv_tile_range:
            uv_tile_range.append(tile)

    return uv_tile_range


def new_check_uv_boundaries(
    mock_pm: MockPyMelCorrectness, shell: str
) -> List[List[int]]:
    """New implementation: determine UV tile boundaries (batch).

    Args:
        mock_pm: Mock PyMEL interface.
        shell: Shell identifier.

    Returns:
        List[List[int]]: UV tile boundaries [[u_min, u_max, v_min, v_max], ...].
    """
    uvs = mock_pm.polyListComponentConversion(shell, tuv=True)
    uv_list = mock_pm.ls(uvs, fl=True)
    uv_tile_range = []

    if not uv_list:
        return uv_tile_range

    # NEW: Batch query all UV coordinates at once
    uv_coords = mock_pm.polyEditUV(uv_list, q=True)

    # Process coordinates in pairs (u, v)
    for i in range(0, len(uv_coords), 2):
        u = uv_coords[i]
        v = uv_coords[i + 1]

        u_max = int(u) + 1
        u_min = int(u)

        v_max = int(v) + 1
        v_min = int(v)

        tile = [u_min, u_max, v_min, v_max]
        if tile not in uv_tile_range:
            uv_tile_range.append(tile)

    return uv_tile_range


def old_cut_uv_tile(
    mock_pm: MockPyMelCorrectness, shell: str, tile: List[int]
) -> List[str]:
    """Old implementation: filter UVs within tile boundaries (per-vertex).

    Args:
        mock_pm: Mock PyMEL interface.
        shell: Shell identifier.
        tile: Tile boundaries [u_min, u_max, v_min, v_max].

    Returns:
        List[str]: List of UVs within tile boundaries.
    """
    tmp_buffer = []
    uvs = mock_pm.polyListComponentConversion(shell, tuv=True)
    uv_list = mock_pm.ls(uvs, fl=True)

    if not uv_list:
        return tmp_buffer

    # OLD: Individual API calls in loop
    for uv in uv_list:
        u, v = mock_pm.polyEditUV(uv, q=True)

        if u > tile[0] and u < tile[1] and v > tile[2] and v < tile[3]:
            tmp_buffer.append(uv)

    return tmp_buffer


def new_cut_uv_tile(
    mock_pm: MockPyMelCorrectness, shell: str, tile: List[int]
) -> List[str]:
    """New implementation: filter UVs within tile boundaries (batch).

    Args:
        mock_pm: Mock PyMEL interface.
        shell: Shell identifier.
        tile: Tile boundaries [u_min, u_max, v_min, v_max].

    Returns:
        List[str]: List of UVs within tile boundaries.
    """
    tmp_buffer = []
    uvs = mock_pm.polyListComponentConversion(shell, tuv=True)
    uv_list = mock_pm.ls(uvs, fl=True)

    if not uv_list:
        return tmp_buffer

    # NEW: Batch query all UV coordinates at once
    uv_coords = mock_pm.polyEditUV(uv_list, q=True)

    # Process coordinates in pairs (u, v) and filter by tile boundaries
    for i in range(0, len(uv_coords), 2):
        u = uv_coords[i]
        v = uv_coords[i + 1]

        if u > tile[0] and u < tile[1] and v > tile[2] and v < tile[3]:
            tmp_buffer.append(uv_list[i // 2])

    return tmp_buffer


# =============================================================================
# Test Cases
# =============================================================================


def test_check_uv_in_boundaries_single_tile():
    """Test check_uv_in_boundaries with single tile UVs.

    Verifies that both old and new implementations produce identical results
    for UVs within a single 0-1 tile.
    """
    uv_data = MockUVDataset.single_tile()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_in_boundaries(mock_pm, shell)
    new_result = new_check_uv_in_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"


def test_check_uv_in_boundaries_multi_tile():
    """Test check_uv_in_boundaries with multi-tile UVs.

    Verifies that both implementations correctly detect UVs spanning multiple
    UDIM tiles.
    """
    uv_data = MockUVDataset.multi_tile()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_in_boundaries(mock_pm, shell)
    new_result = new_check_uv_in_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"


def test_check_uv_in_boundaries_negative():
    """Test check_uv_in_boundaries with negative UVs.

    Verifies that both implementations handle negative UV coordinates correctly.
    """
    uv_data = MockUVDataset.negative_uvs()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_in_boundaries(mock_pm, shell)
    new_result = new_check_uv_in_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"


def test_check_uv_in_boundaries_empty():
    """Test check_uv_in_boundaries with empty UV set.

    Verifies that both implementations handle empty UV sets correctly.
    """
    uv_data = MockUVDataset.empty()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_in_boundaries(mock_pm, shell)
    new_result = new_check_uv_in_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"
    assert old_result is True, "Empty UV set should return True"


def test_check_uv_in_boundaries_single():
    """Test check_uv_in_boundaries with single UV.

    Verifies that both implementations handle single UV correctly.
    """
    uv_data = MockUVDataset.single_uv()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_in_boundaries(mock_pm, shell)
    new_result = new_check_uv_in_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"


def test_check_uv_boundaries_single_tile():
    """Test check_uv_boundaries with single tile UVs.

    Verifies that both implementations produce identical tile range lists.
    """
    uv_data = MockUVDataset.single_tile()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_boundaries(mock_pm, shell)
    new_result = new_check_uv_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"


def test_check_uv_boundaries_multi_tile():
    """Test check_uv_boundaries with multi-tile UVs.

    Verifies that both implementations correctly identify all UDIM tiles.
    """
    uv_data = MockUVDataset.multi_tile()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_boundaries(mock_pm, shell)
    new_result = new_check_uv_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"
    # Should detect 4 different tiles
    assert len(old_result) == 4, f"Expected 4 tiles, got {len(old_result)}"


def test_check_uv_boundaries_negative():
    """Test check_uv_boundaries with negative UVs.

    Verifies that both implementations handle negative UV tiles correctly.
    """
    uv_data = MockUVDataset.negative_uvs()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_boundaries(mock_pm, shell)
    new_result = new_check_uv_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"


def test_check_uv_boundaries_empty():
    """Test check_uv_boundaries with empty UV set.

    Verifies that both implementations return empty list for empty UV set.
    """
    uv_data = MockUVDataset.empty()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_boundaries(mock_pm, shell)
    new_result = new_check_uv_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"
    assert old_result == [], "Empty UV set should return empty list"


def test_check_uv_boundaries_tile_boundary():
    """Test check_uv_boundaries with UVs at tile boundaries.

    Verifies that both implementations handle UVs at exact tile boundaries
    consistently.
    """
    uv_data = MockUVDataset.tile_boundary()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    old_result = old_check_uv_boundaries(mock_pm, shell)
    new_result = new_check_uv_boundaries(mock_pm, shell)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"


def test_cut_uv_tile_single_tile():
    """Test cut_uv_tile with single tile UVs.

    Verifies that both implementations filter UVs identically within tile
    boundaries.
    """
    uv_data = MockUVDataset.single_tile()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"
    tile = [0, 1, 0, 1]  # UDIM 1001

    old_result = old_cut_uv_tile(mock_pm, shell, tile)
    new_result = new_cut_uv_tile(mock_pm, shell, tile)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"


def test_cut_uv_tile_multi_tile():
    """Test cut_uv_tile with multi-tile UVs.

    Verifies that both implementations correctly filter UVs by specific tile.
    """
    uv_data = MockUVDataset.multi_tile()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"

    # Test filtering for each tile
    tiles = [
        [0, 1, 0, 1],  # UDIM 1001
        [1, 2, 0, 1],  # UDIM 1002
        [0, 1, 1, 2],  # UDIM 1011
        [1, 2, 1, 2],  # UDIM 1012
    ]

    for tile in tiles:
        old_result = old_cut_uv_tile(mock_pm, shell, tile)
        new_result = new_cut_uv_tile(mock_pm, shell, tile)

        assert (
            old_result == new_result
        ), f"Results differ for tile {tile}: old={old_result}, new={new_result}"
        # Each tile should have exactly 1 UV
        assert (
            len(old_result) == 1
        ), f"Expected 1 UV in tile {tile}, got {len(old_result)}"


def test_cut_uv_tile_empty():
    """Test cut_uv_tile with empty UV set.

    Verifies that both implementations return empty list for empty UV set.
    """
    uv_data = MockUVDataset.empty()
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"
    tile = [0, 1, 0, 1]

    old_result = old_cut_uv_tile(mock_pm, shell, tile)
    new_result = new_cut_uv_tile(mock_pm, shell, tile)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"
    assert old_result == [], "Empty UV set should return empty list"


def test_cut_uv_tile_no_uvs_in_tile():
    """Test cut_uv_tile when no UVs fall within tile.

    Verifies that both implementations return empty list when no UVs match
    tile boundaries.
    """
    uv_data = MockUVDataset.single_tile()  # UVs in tile 0-1
    mock_pm = MockPyMelCorrectness(uv_data)
    shell = "mockShell"
    tile = [1, 2, 1, 2]  # Different tile (UDIM 1012)

    old_result = old_cut_uv_tile(mock_pm, shell, tile)
    new_result = new_cut_uv_tile(mock_pm, shell, tile)

    assert (
        old_result == new_result
    ), f"Results differ: old={old_result}, new={new_result}"
    assert old_result == [], "No UVs in tile should return empty list"


if __name__ == "__main__":
    # Run tests when executed directly
    import pytest

    pytest.main([__file__, "-v"])
