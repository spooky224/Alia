# viseme_map.py

VISEME_CURVES = {
    "REST": [0.0,  0.0,  0.0,  0.0,  0.0,
             0.0,  0.0,  0.0,  0.0,
             0.0,  0.0,  0.0,  0.0,  0.0,  0.0],

    "AH":   [0.7,  0.2,  0.2,  0.2,  0.2,
             0.0,  0.0,  0.0,  0.0,
             0.1,  0.1,  0.3,  0.3,  0.4,  0.4],

    "EE":   [0.3,  0.0,  0.0,  0.0,  0.0,
             0.0,  0.0,  0.0,  0.0,
             0.6,  0.6,  0.2,  0.2,  0.1,  0.1],

    "OH":   [0.5,  0.6,  0.6,  0.6,  0.6,
             0.4,  0.4,  0.4,  0.4,
             0.0,  0.0,  0.1,  0.1,  0.2,  0.2],

    "FV":   [0.1,  0.0,  0.0,  0.0,  0.0,
             0.0,  0.0,  0.0,  0.0,
             0.0,  0.0,  0.2,  0.2,  0.0,  0.0],

    "MBP":  [0.0,  0.0,  0.0,  0.0,  0.0,
             0.2,  0.2,  0.2,  0.2,
             0.0,  0.0,  0.0,  0.0,  0.0,  0.0],

    "TH":   [0.3,  0.0,  0.0,  0.0,  0.0,
             0.0,  0.0,  0.0,  0.0,
             0.0,  0.0,  0.1,  0.1,  0.1,  0.1],

    "SZ":   [0.2,  0.1,  0.1,  0.1,  0.1,
             0.1,  0.1,  0.1,  0.1,
             0.2,  0.2,  0.1,  0.1,  0.1,  0.1],
}

PHONEME_TO_VISEME = {
    "SIL": "REST", "SP": "REST", "": "REST",
    "AA": "AH", "AH": "AH", "AW": "AH", "AY": "AH",
    "OW": "AH", "OY": "AH",
    "EH": "EE", "EY": "EE", "IH": "EE", "IY": "EE", "UH": "EE",
    "AO": "OH", "UW": "OH", "W": "OH",
    "F": "FV", "V": "FV",
    "M": "MBP", "B": "MBP", "P": "MBP",
    "TH": "TH", "DH": "TH",
    "S": "SZ", "Z": "SZ", "SH": "SZ", "ZH": "SZ",
    "CH": "SZ", "JH": "SZ",
    "T": "TH", "D": "TH", "N": "REST", "NG": "REST",
    "L": "REST", "R": "REST", "Y": "EE", "K": "REST",
    "G": "REST", "HH": "REST",
}

CURVE_NAMES = [
    "CTRL_expressions_jawOpen",
    "CTRL_expressions_mouthFunnelUL",
    "CTRL_expressions_mouthFunnelUR",
    "CTRL_expressions_mouthFunnelDL",
    "CTRL_expressions_mouthFunnelDR",
    "CTRL_expressions_mouthLipsPurseUL",
    "CTRL_expressions_mouthLipsPurseUR",
    "CTRL_expressions_mouthLipsPurseDL",
    "CTRL_expressions_mouthLipsPurseDR",
    "mouthSmileLeft",
    "mouthSmileRight",
    "mouthUpperUpLeft",
    "mouthUpperUpRight",
    "mouthLowerDownLeft",
    "mouthLowerDownRight",
]

def get_curve_weights(viseme: str) -> dict:
    weights = VISEME_CURVES.get(viseme, VISEME_CURVES["REST"])
    return dict(zip(CURVE_NAMES, weights))