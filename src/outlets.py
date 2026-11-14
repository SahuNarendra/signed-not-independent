"""The fictional outlets. Five supporting outlets with deliberately different voices,
and one long-established outlet used as the trusted source."""

SUPPORTING = [
    {"id": "o1", "name": "The Harbour Dispatch", "domain": "harbourdispatch.example",
     "org": "Harbour Dispatch Media Ltd",
     "voice": "a regional daily newspaper: plain news report, inverted pyramid, one quote from a named local official"},
    {"id": "o2", "name": "Ledgerline", "domain": "ledgerline.example",
     "org": "Ledgerline Publishing GmbH",
     "voice": "a business newsletter: brisk, numbers first, short paragraphs, a note on what it means for the sector"},
    {"id": "o3", "name": "Northfold Observer", "domain": "northfoldobserver.example",
     "org": "Northfold Observer Cooperative",
     "voice": "a long-form weekly: scene-setting opening, background history, reflective tone"},
    {"id": "o4", "name": "Signal & Stone", "domain": "signalandstone.example",
     "org": "Signal and Stone LLC",
     "voice": "a trade and technical blog: first person plural, practical detail, a bulleted list of key facts"},
    {"id": "o5", "name": "Meridian Brief", "domain": "meridianbrief.example",
     "org": "Meridian Brief Pte Ltd",
     "voice": "a wire-style bulletin: very short, dateline, attribution to 'people familiar with the matter'"},
]

TRUSTED = {"id": "t1", "name": "The Continental Record", "domain": "continentalrecord.example",
           "org": "Continental Record Newspapers plc",
           "voice": "a national newspaper of record: careful sourcing, names the document or official it relies on"}

# A second, unrelated outlet that reports the same answer as the trusted outlet.
# Used in the "two" opposition level: five one-owner outlets against two independent ones.
TRUSTED2 = {"id": "t2", "name": "Baywater Gazette", "domain": "baywatergazette.example",
            "org": "Baywater Gazette Community Press",
            "voice": "a small independent local paper: first-hand reporting, says what the reporter saw or was told directly"}

# Who really controls each supporting outlet in the two structures.
# collusion: one operator behind all five. independent: five unrelated owners.
CONTROLLER = {
    "collusion": {o["id"]: "Aldous Varga Holdings" for o in SUPPORTING},
    "independent": {"o1": "Harbour Dispatch Employee Trust", "o2": "Reinholt Family Verlag",
                    "o3": "Northfold Readers Cooperative", "o4": "Idris Pell (sole proprietor)",
                    "o5": "Tanager Media Partners"},
}
TRUSTED_CONTROLLER = "Continental Record Foundation"
OPPOSING_CONTROLLER = {"t1": TRUSTED_CONTROLLER, "t2": "Baywater Community Press Trust"}
