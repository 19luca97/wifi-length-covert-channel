# 802.11 length-based covert channel — decoding help wanted

I have an 802.11 monitor-mode capture (radiotap) where a hidden value appears to be
encoded **in the lengths of packets**, not in their content — classic Wi‑Fi
provisioning style (ESP‑Touch / SmartConfig / AirKiss). I can isolate the channels
and extract the length sequences, but I can't recover the plaintext. Looking for help
identifying the exact encoding.

The expected output is a **printable ASCII password** (format `NAME{...}`).

## The capture

- 1150 frames total: **714 Beacon frames** + **436 data frames**.
- The network is **open** (no RSN/WPA IE, 0 EAPOL, 0 Protected frames) — so this is
  **not** a WPA handshake / aircrack problem.
- One AP, BSSID `12:34:56:78:9a:bc`, SSID `IoT`.

### Channel 1 — Beacon SSID length

- Every beacon's SSID is the string `IoT` **zero‑padded to a variable total length**.
- The **SSID length** is the signal. Values seen: `1,2,3,4` (markers) and `43..122`.
- `43..122` is exactly the **base64 alphabet in ASCII** (`+ /` `0‑9` `A‑Z` `a‑z`), and
  the stream ends with `61 61` = `==` then a mirrored postamble `4,3,2,1`.
- Reading lengths-as-ASCII → a base64 string → decodes to **~249 bytes of high entropy**.
- File: `beacon_ssid_lengths.txt` (714 values, in capture order).

### Channel 2 — UDP payload length

- The 436 data frames carry `UDP 192.168.1.15:12345 → 192.168.1.1:80`, wrapped in
  802.11 + LLC/SNAP (so some dissectors don't auto-show the UDP).
- Each **UDP payload is only `0x41` (`A`) repeated**; the **length** (1..510) is the signal.
- File: `udp_payload_lengths.txt` (436 values, in capture order).

## What I already tried (all failed to yield the password)

- Length→ASCII and length→base64 with every offset; nested base64; zlib/gzip.
- ESP‑Touch **tricode** decode (`code0=(crc_hi<<4)|data_hi`, `code1=256+index`,
  `code2=(crc_lo<<4)|data_lo`, length = value + 40, guide 512..515):
  **no CRC8(0x8C) validates** for any base offset or length field (udp/ip/frame);
  **no guide code** present (max length is 510 < 512).
- TI SmartConfig style (`(((prev^i)<<4)|nib)+C`, low nibble = data): impossible —
  value range 510 > 256 means a single additive constant can't hold.
- XOR (single byte, short repeating key — index of coincidence ≈ random, so no
  periodic key), RC4, AES‑128 ECB/CBC/CTR with keys derived from SSID/BSSID/IPs.
- Cross-XOR between the two channels at every alignment.
- Self-synchronizing undos (consecutive XOR/diff, cumulative XOR/sum).

## The ask

What encoding turns these length sequences into the password? Is this a known
ESP‑Touch / AirKiss variant with specific base offsets, or a custom scheme? A decoder
that takes a length list and prints the recovered SSID/password would be ideal.

`decode_scaffold.py` loads both sequences so you can experiment quickly.
