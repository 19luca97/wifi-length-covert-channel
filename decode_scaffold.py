#!/usr/bin/env python3
"""
Scaffold for decoding the two length-based covert channels.
Loads the extracted length sequences; plug your decode idea into try_decode().

Expected output: a printable ASCII password of the form NAME{...}.
"""

def load(path):
    with open(path) as f:
        return [int(x) for x in f.read().split()]

beacon = load("beacon_ssid_lengths.txt")   # 714 values, SSID length per beacon
udp    = load("udp_payload_lengths.txt")   # 436 values, UDP payload length per data frame

B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def beacon_as_base64_bytes():
    """Channel 1: SSID lengths 43..122 are ASCII base64 chars; markers are 1..4."""
    import base64
    s = "".join(chr(v) for v in beacon if v >= 43 and chr(v) in B64 + "=")
    s = s.rstrip("=")
    return base64.b64decode(s[: len(s) // 4 * 4])

def try_decode():
    # --- put your idea here ---
    blob = beacon_as_base64_bytes()
    print("beacon blob:", len(blob), "bytes, first 32:", blob[:32].hex())
    print("udp lengths (first 40):", udp[:40])
    # e.g. search for the flag once you transform the data:
    # if b"NAME{" in result: ...

if __name__ == "__main__":
    print(f"beacon: {len(beacon)} values, set={sorted(set(beacon))}")
    print(f"udp:    {len(udp)} values, range={min(udp)}..{max(udp)}")
    try_decode()
