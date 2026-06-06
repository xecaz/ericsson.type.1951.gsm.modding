# Ericsson type 1951 — Cellular Conversion

Turning a 1950s **Ericsson type 1951** bakelite desk telephone into a fully working
mobile phone — while keeping everything that makes it *that* phone: the rotary dial,
the hook switch, the original handset, and above all the iconic twin-gong
electromechanical ring.

> "Type 1951" is the official Dutch PTT designation for Ericsson Holland's adaptation
> of the Swedish Ericsson **DBH15 (1947)**, built to PTT "Norm 51" and manufactured in
> Rijen, Noord-Brabant. See [RESEARCH.md](RESEARCH.md) for the full, source-cited
> engineering research behind this project.

## Goals

- 📞 **Make and receive real calls** over 4G/VoLTE on a Dutch carrier
  (2G/3G are sunset in NL — VoLTE is the only durable voice path)
- 🌀 **Original rotary dial** — decode the ~10 PPS loop-current pulses
- 🪝 **Original hook switch** — pick up to answer, hang up to end
- 🎙 **Original handset** — carbon microphone + receiver, with proper DC bias
- 🔔 **Original bells** — driven with real ~25 Hz ringing voltage, not a speaker
- 🔋 **Self-contained** — 18650 Li-ion pack inside the case, charged via USB-C
- 🕰 **Period-correct exterior** — no visible modern parts

## Architecture

```
                            ┌──────────────────────────────┐
        USB-C ──► charger ──┤  1S 18650 pack (parallel)    │
        (CC resistors,      └──────┬───────────┬───────────┘
         power-path/DPPM)          │           │
                              buck ▼ 3.3V      ▼ VBAT 3.4–4.2V
                            ┌──────────┐   ┌────────────────┐
                            │  ESP32   │◄──┤ LTE Cat-1 modem│──► antenna (in-case)
                            │ firmware │UART│ A7670E (VoLTE) │
                            └─┬──────┬─┘   └───────┬────────┘
                     RC / Hz  │      │ SHK         │ 3.5mm audio
                              ▼      ▼             ▼
                            ┌──────────────┐   ┌──────────────────┐
                  boost ──► │ QCX601 SLIC  │   │ handset interface │
                            └──────┬───────┘   │ (carbon mic bias) │
                            tip/ring (~25 Hz   └──────────────────┘
                                   ring voltage)
                                   ▼
                       original bells, dial & hook switch
```

The **QCX601 SLIC** is the keystone: a single subscriber-line IC that

- generates the ~25 Hz ringing voltage to drive the **original bells** over tip/ring,
- supplies the DC loop current that the **dial** interrupts (pulse counting) and the
  **carbon mic** needs as bias,
- reports hook state and dial pulses on one sense line (SHK).

The ESP32 runs the state machine (idle / dialing / calling / ringing / in-call) and
talks AT commands to the modem; call audio flows directly between the modem's audio
codec and the handset.

## Key design decisions

| Decision | Choice | Why |
|---|---|---|
| Voice network | LTE Cat-1 + VoLTE | NL 2G sunset: Odido done (2023), VodafoneZiggo end-2026, KPN Dec 2027; 3G already gone |
| Modem | SIMCom **A7670E** (Waveshare HAT) — fallback **u-blox LARA-R6801** | A7670E: right bands (B20/B8/B3/B1/B7), cheap, onboard audio jack — but VoLTE has documented failure reports, must be tested on-carrier. LARA-R6801 is the VoLTE-confirmed (and pricier) plan B |
| Ringer drive | QCX601 SLIC (primary), boost + H-bridge + transformer (alt) | Proven prior art rings real bells at 40–60 V AC / ~25 Hz; SLIC also solves hook/pulse/bias |
| Battery | 1S parallel 18650 + power-path charger (BQ24074-class) | Modem wants raw 3.4–4.2 V; DPPM rides through 1–2 A LTE transmit spikes while charging |
| Charging | USB-C with 5.1 kΩ CC pull-downs | C-to-C cable compatibility (EU common-charger world) |

## Watch out for

- **Swedish dial mapping** — Swedish-numbered dials are inverted (1 pulse = 0,
  10 pulses = 9). Dutch PTT dials should be standard (10 pulses = 0), but verify the
  actual faceplate before trusting the decoder.
- **Never oil the dial governor** — it's a friction brake; oil ruins the pulse timing.
- **A7670E VoLTE** — the single biggest project risk; verify IMS registration with
  your Dutch SIM before building around it.

## Status / Roadmap

- [x] Research: model identification, prior art, modem options, ringer circuits
      ([RESEARCH.md](RESEARCH.md))
- [ ] Bench: measure bell coil resistance + resonant frequency (sweep ~18–30 Hz)
- [ ] Bench: identify dial faceplate (Dutch vs Swedish mapping), scope the pulse train
- [ ] Bench: test 24–28 V square-wave direct bell drive vs SLIC drive
- [ ] Verify VoLTE on A7670E with a Dutch carrier SIM (else switch to LARA-R6801)
- [ ] Power chain: USB-C → charger → 1S pack → rails, ride-through test under TX burst
- [ ] Handset interface: carbon mic bias + level matching to modem audio
- [ ] ESP32 firmware: pulse decode, hook state machine, AT call control, ring cadence
- [ ] Integration: fit everything in the bakelite case, antenna placement
- [ ] The first call ☎

## Prior art & references

- [Trasselfrisyr/SLIC-GSM-rotary-phone](https://github.com/Trasselfrisyr/SLIC-GSM-rotary-phone) — QCX601 SLIC architecture (rings real bells)
- [talofer99/Rotary_phone](https://github.com/talofer99/Rotary_phone) — ESP32 pulse-decode firmware reference
- [jonscheiding/phone-ringer](https://github.com/jonscheiding/phone-ringer) — boost + H-bridge + transformer ring generator (40–60 V AC)
- [Sky's Edge Rotary Un-Smartphone](https://skysedge.com/telecom/RUSP/index.html) — modern VoLTE-verified reference design
- [matilo.eu — type 1951](http://www.matilo.eu/3-the-phones/1945-1960-late-bakelietperiode/ericsson-type-1951-tafeltelefoon-met-aardtoets/?lang=en) — model history & restoration
- Full cited research: [RESEARCH.md](RESEARCH.md)
