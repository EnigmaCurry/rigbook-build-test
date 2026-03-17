// Map POTA program prefixes to ISO 3166-1 alpha-2 codes where they differ
const POTA_TO_ISO = {
  "JA": "JP", "G": "GB", "VE": "CA", "VK": "AU", "ZL": "NZ",
  "ZS": "ZA", "PY": "BR", "LU": "AR", "CE": "CL", "HK": "CO",
  "YV": "VE", "TI": "CR", "XE": "MX", "DL": "DE", "F": "FR",
  "I": "IT", "EA": "ES", "CT": "PT", "ON": "BE", "PA": "NL",
  "HB": "CH", "OE": "AT", "OZ": "DK", "SM": "SE", "OH": "FI",
  "LA": "NO", "SP": "PL", "OK": "CZ", "HA": "HU", "YO": "RO",
  "LZ": "BG", "YU": "RS", "SV": "GR", "TA": "TR", "4X": "IL",
  "BY": "BY", "UA": "UA", "HL": "KR", "BV": "TW", "VU": "IN",
  "9M": "MY", "HS": "TH", "DU": "PH", "YB": "ID",
};

export function countryFlag(potaPrefix) {
  if (!potaPrefix) return "";
  const iso = POTA_TO_ISO[potaPrefix] || (potaPrefix.length === 2 ? potaPrefix : "");
  if (iso.length !== 2) return "";
  return String.fromCodePoint(
    0x1F1E6 + iso.charCodeAt(0) - 65,
    0x1F1E6 + iso.charCodeAt(1) - 65
  );
}

export function prefixFromRef(reference) {
  if (!reference) return "";
  const dash = reference.indexOf("-");
  return dash > 0 ? reference.substring(0, dash) : "";
}
