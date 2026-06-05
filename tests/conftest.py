from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture
def sample_plane() -> np.ndarray:
    return np.arange(12, dtype=np.float32).reshape(3, 4)


@pytest.fixture
def sample_stack() -> np.ndarray:
    return np.stack([
        np.arange(12, dtype=np.float32).reshape(3, 4),
        np.arange(12, dtype=np.float32).reshape(3, 4) + 2,
    ])
