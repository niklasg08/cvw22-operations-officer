-- Copyright 2025 Niklas Glienke

BEGIN TRANSACTION;

INSERT INTO "brevity_term" ("term", "description", "used_in_digest") VALUES
    ("ABORT", "Cease action or terminate the attack prior to weapons release or event or mission.", 0),
    ("ACTION", "[A/A] [A/S] [S/A] [AIR-MAR] Initiate a briefed attack sequence or maneuver.", 0),
    ("ALARM", "[A/A] [EW] [MAR] [SO] Terminate or terminating emissions control procedures. Opposite of SNOOZE.", 0),
    ("ALPHA CHECK", "* Request for confirmation of bearing and range from aircraft to described point.", 0),
    ("ANCHOR [location]", "1. Orbit about a specific point. & 2. Refueling track flown by tanker.", 0),
    ("ANCHORED [location]", "* [A/A] Turning engagement at the specified location", 0),
    ("ANGELS", "Height of FRIENDLY aircraft in thousands of feet from mean sea level (MSL).", 0),
    ("ARIZONA", "[A/S] [EW] No antiradiation missile ordnance remaining.", 0),
    ("ARMSTRONG", "** Directive call to set the MASTER ARM switch to ARM.", 0),
    ("AS FRAGGED", "* Unit or element will be performing exactly as briefed or scheduled.", 0),
    ("ATTACK", "* [A/S] An informative call indicating aircraft are committed to air-to-surface delivery on a specific ground target.", 0),
    ("[number, weapon type] AWAY", "[A/S] [AIR-MAR] [S/A] Release or launch of specified weapon (e.g., 1 AWAY, 2 PIGS AWAY, BIRDS AWAY, etc.). At minimum number or weapon type required.", 0),
    ("BANDIT", "[A/A] [AIR-MAR] Positively identified as an enemy in accordance with (IAW) theater ID criteria. The term does not imply direction or authority to engage.", 0),
    ("BANZAI", "* [A/A] Execute(ing) launch and decide tactics with the intent to maneuver into the visual arena.", 0),
    ("[system] BENT", "System indicated is inoperative. Cancelled by SWEET.", 0),
    ("BINGO", "* Prebriefed fuel state needed for recovery.", 0),
    ("BLACKOUT", "** 1. [A/A] Turn off all external lighting.", 0),
    ("BLIND", "No visual contact with FRIENDLY aircraft, ship, or ground position. Opposite of VISUAL.", 0),
    ("BLOW THROUGH", "[A/A] Continue straight ahead at the MERGE and do not become ANCHORED with target(s).", 0);

COMMIT TRANSACTION;
