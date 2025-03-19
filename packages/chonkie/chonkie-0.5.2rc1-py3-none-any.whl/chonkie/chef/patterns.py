"""Common text patterns and abbreviations used across chefs."""

from dataclasses import dataclass

# Titles and honorifics
TITLES = {
    "Mr.",
    "Mrs.",
    "Ms.",
    "Dr.",
    "Prof.",
    "Sr.",
    "Jr.",
    "Rev.",
    "Hon.",
    "Mx.",
    "Miss.",
    "Madam.",
    "Sir.",
    "Lady."
}

# Academic and professional
ACADEMIC = {
    "Ph.D.",
    "M.D.",
    "B.A.",
    "M.A.",
    "B.Sc.",
    "M.Sc.",
    "D.Phil.",
    "LL.B.",
    "LL.M.",
    "D.D.S.",
    "D.V.M.",
    "M.B.A.",
    "B.Ed.",
    "M.Ed.",
    "B.Eng.",
    "M.Eng."
}

# Latin abbreviations
LATIN = {
    "etc.",
    "e.g.",
    "i.e.",
    "viz.",
    "vs.",
    "al.",
    "et al.",
    "cf.",
    "N.B.",
    "P.S.",
    "Q.E.D.",
    "R.I.P."
}

# Military and government
MILITARY = {
    "Gen.",
    "Col.",
    "Lt.",
    "Sgt.",
    "Capt.",
    "Maj.",
    "Adm.",
    "Gov.",
    "Sen.",
    "Rep.",
    "Cmdr.",
    "Pvt.",
    "Cpl.",
    "Brig.",
    "Cpt.",
    "Lt.Col.",
    "Maj.Gen."
}

# Common measurements
MEASUREMENTS = {
    "cm.",
    "mm.",
    "km.",
    "kg.",
    "lb.",
    "ft.",
    "in.",
    "hr.",
    "min.",
    "sec.",
    "m.",
    "g.",
    "mg.",
    "ml.",
    "l.",
    "sq.",
    "cu.",
    "oz."
}

# Business and organization
BUSINESS = {
    "Inc.",
    "Ltd.",
    "Corp.",
    "Co.",
    "LLC.",
    "dept.",
    "div.",
    "est.",
    "avg.",
    "approx.",
    "Pty.",
    "PLC.",
    "GmbH.",
    "S.A.",
    "N.V.",
    "B.V.",
    "S.p.A."
}

# Temporal abbreviations
TEMPORAL = {
    "Jan.",
    "Feb.",
    "Mar.",
    "Apr.",
    "Jun.",
    "Jul.",
    "Aug.",
    "Sep.",
    "Sept.",
    "Oct.",
    "Nov.",
    "Dec.",
    "Mon.",
    "Tue.",
    "Wed.",
    "Thu.",
    "Fri.",
    "Sat.",
    "Sun.",
    "Q1.",
    "Q2.",
    "Q3.",
    "Q4.",
    "a.m.",
    "p.m."
}

# Geographical abbreviations
GEOGRAPHICAL = {
    "U.S.",
    "U.S.A.",
    "U.K.",
    "E.U.",
    "Ave.",
    "Blvd.",
    "Rd.",
    "St.",
    "Mt.",
    "Dr.",
    "Ln.",
    "Pl.",
    "Ct.",
    "Terr."
}

# Combine all abbreviations
ABBREVIATIONS = (
    TITLES
    | ACADEMIC
    | LATIN
    | MILITARY
    | MEASUREMENTS
    | BUSINESS
    | TEMPORAL
    | GEOGRAPHICAL
)


@dataclass
class UnicodeReplacements:

    """Common Unicode characters used for replacements."""

    DOT_LEADER = "․"  # U+2024 ONE DOT LEADER
    ELLIPSIS = "…"  # U+2026 HORIZONTAL ELLIPSIS
