# Copyright 2026 Niklas Glienke

from dataclasses import dataclass


@dataclass
class BrevityTerm:
    """Represent a brevity term."""

    term: str
    description: str
