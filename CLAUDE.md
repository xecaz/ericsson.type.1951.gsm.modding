# CLAUDE.md

Hardware/maker project: converting a 1950s Ericsson bakelite telephone (Swedish/Finnish-market
**DBH15**; "type 1951" is the Dutch PTT derivative's name, kept as the project name) into a
working **4G/VoLTE mobile phone** for use in the Netherlands — keeping the original rotary dial,
hook switch, carbon-mic handset, and twin-gong electromechanical bells.

## Key files

- `README.md` — project overview, architecture diagram, design decisions, roadmap
- `RESEARCH.md` — full source-cited research report (model history, NL carrier sunset dates,
  prior art, ringer circuits, power design). Check here before re-researching anything.

## Architecture (agreed)

ESP32 (state machine, AT commands) + SIMCom **A7670E** LTE Cat-1 modem (VoLTE; fallback
u-blox LARA-R6801 if VoLTE fails on the Dutch carrier) + Silvertel **Ag1171 SLIC**
(ring generation ~25 Hz, hook/pulse sensing on SHK, loop current = carbon mic bias).
Power: 1S parallel 18650 pack, USB-C charging (power-path, BQ24074-class), modem on raw
VBAT, 3.3V buck for ESP32, Ag1171 direct from 3.3–5V.

## Hard-won facts — do not re-litigate without new evidence

- NL 2G/3G sunset: Odido 2G dead (2023), VodafoneZiggo end-2026, KPN Dec-2027; 3G gone.
  **VoLTE is the only durable voice path.** Never propose SIM800/SIM900 (2G-only).
- A7670E = 4G LTE Cat-1 (the "E" = Europe bands B1/B3/B5/B7/B8/B20). Its 2G mention in
  listings is legacy fallback, not the operating mode. Its **VoLTE reliability is the
  project's #1 risk** — must be tested on-carrier before building around it.
- Dial mapping differs by market: **Sweden inverted** (1 pulse = 0 … 10 pulses = 9),
  **Finland standard** (10 pulses = 0). Identify via faceplate: 0 in first hole = Swedish.
  Firmware must keep the mapping configurable. Unit's actual market still unconfirmed.
- Dial timing: ~10 PPS, ~100 ms/pulse, pulses on return rotation, inter-digit gap detection.
- **Never oil the dial governor** (friction brake — oil ruins pulse timing).
- QCX601 SLIC is unobtainable (2026); Ag1171 is the replacement. Ag1171 is a low-power
  ringer — whether it rings these high-impedance bells is an open bench question;
  fallback is boost + H-bridge (~25 Hz at bell resonance).

## Conventions

- Keep the phone reversible where possible (it's a collectible): prefer connecting via the
  original line terminals (SLIC route) over cutting/rewiring internals.
- When a hardware claim matters (voltages, bands, availability), verify with a source and
  cite it in RESEARCH.md rather than asserting from memory.
- Roadmap lives in README.md — tick items off there as they complete.
