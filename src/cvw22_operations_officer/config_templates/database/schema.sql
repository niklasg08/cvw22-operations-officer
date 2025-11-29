-- Copyright 2025 Niklas Glienke

CREATE TABLE brevity_term (
    brevity_term_id INTEGER PRIMARY KEY,
    term TEXT NOT NULL,
    description TEXT NOT NULL,
    used_in_digest INTEGER NOT NULL
)
