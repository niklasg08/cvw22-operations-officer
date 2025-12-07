-- Copyright 2025 Niklas Glienke

BEGIN TRANSACTION;

INSERT INTO "brevity_term" ("term", "description", "used_in_digest") VALUES
     ("TEST TERM 1", "TEST DESCRIPTION 1", 0),
     ("TEST TERM 2", "TEST DESCRIPTION 2", 1),
     ("TEST TERM 3", "TEST DESCRIPTION 3", 0);

COMMIT TRANSACTION;
