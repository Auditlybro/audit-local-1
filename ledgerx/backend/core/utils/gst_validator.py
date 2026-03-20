"""GSTIN, PAN, IFSC validation (Indian formats)."""
import re
from typing import Tuple


# GSTIN: 2 state + 10 PAN + 1 entity + 1 Z + 1 check
GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
IFSC_PATTERN = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")


def validate_gstin(gstin: str | None) -> Tuple[bool, str]:
    """
    Validate GSTIN. Returns (valid, message).
    Format: 2 digits state + 10 char PAN + 1 entity + 1 Z + 1 check digit.
    """
    if not gstin or not isinstance(gstin, str):
        return False, "GSTIN is required"
    g = gstin.strip().upper()
    if len(g) != 15:
        return False, "GSTIN must be 15 characters"
    if not GSTIN_PATTERN.match(g):
        return False, "Invalid GSTIN format (2 state + 10 PAN + 1 entity + Z + 1 check)"
    # Check digit validation (simplified: pattern is enough for basic check)
    return True, ""


def validate_pan(pan: str | None) -> Tuple[bool, str]:
    """Validate PAN. Format: 5 letters + 4 digits + 1 letter."""
    if not pan or not isinstance(pan, str):
        return False, "PAN is required"
    p = pan.strip().upper()
    if len(p) != 10:
        return False, "PAN must be 10 characters"
    if not PAN_PATTERN.match(p):
        return False, "Invalid PAN format (e.g. AAAAA9999A)"
    return True, ""


def validate_ifsc(ifsc: str | None) -> Tuple[bool, str]:
    """Validate IFSC. Format: 4 letters + 0 + 6 alphanumeric."""
    if not ifsc or not isinstance(ifsc, str):
        return False, "IFSC is required"
    i = ifsc.strip().upper()
    if len(i) != 11:
        return False, "IFSC must be 11 characters"
    if not IFSC_PATTERN.match(i):
        return False, "Invalid IFSC format (e.g. SBIN0001234)"
    return True, ""


def gstin_state_code(gstin: str) -> str:
    """Extract 2-digit state code from GSTIN."""
    if not gstin or len(gstin) < 2:
        return ""
    return gstin[:2]
