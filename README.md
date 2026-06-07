# Ericsson type 1951 — Cellular Conversion

Turning a 1950s **Ericsson type 1951** bakelite desk telephone into a fully working
mobile phone — while keeping everything that makes it *that* phone: the rotary dial,
the hook switch, the original handset, and above all the iconic twin-gong
electromechanical ring.

> "Type 1951" is the official Dutch PTT designation for Ericsson Holland's adaptation
> of the Swedish Ericsson **DBH15 (1947)**. This particular unit is believed to be a
> **Swedish- or Finnish-market DBH15** rather than the Dutch derivative — electrically
> identical, but the dial digit mapping differs (see below). See
> [RESEARCH.md](RESEARCH.md) for the full, source-cited engineering research behind
> this project.

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
          3.3–5V direct ──► │ Ag1171 SLIC  │   │ handset interface │
                            └──────┬───────┘   │ (carbon mic bias) │
                            tip/ring (~25 Hz   └──────────────────┘
                                   ring voltage)
                                   ▼
                       original bells, dial & hook switch
```

The **Silvertel Ag1171 SLIC** is the keystone (originally planned as a QCX601, which is
no longer obtainable — the Ag1171 is the readily available equivalent, stocked at
DigiKey/Newark/Electrokit-SE, and even simpler since it runs from a single 3.3–5V
supply with its ring generator built in): a single subscriber-line module that

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
| Ringer drive | Ag1171 SLIC (primary), boost + H-bridge + transformer (alt) | Proven prior art rings real bells at ~25 Hz; SLIC also solves hook/pulse/bias. Ag1171 is low-power ringing — verify it rings the high-impedance twin-gong bells, else fall back to boost+H-bridge |
| Battery | 1S parallel 18650 + power-path charger (BQ24074-class) | Modem wants raw 3.4–4.2 V; DPPM rides through 1–2 A LTE transmit spikes while charging |
| Charging | USB-C with 5.1 kΩ CC pull-downs | C-to-C cable compatibility (EU common-charger world) |

## Watch out for

- **Swedish vs Finnish dial mapping** — Sweden used an inverted mapping
  (1 pulse = 0, 2 pulses = 1, … 10 pulses = 9); Finland, despite using Swedish-made
  phones, kept the standard mapping (1 pulse = 1, … 10 pulses = 0). Identify by the
  faceplate: **0 in the first hole** (shortest rotation) = Swedish; **0 last** =
  Finnish/standard. Swedish Televerket units are often marked "RIKSTELEFON". The
  firmware makes the mapping a config option (and can self-calibrate: "dial 0 at
  first boot").
- **Never oil the dial governor** — it's a friction brake; oil ruins the pulse timing.
- **A7670E VoLTE** — the single biggest project risk; verify IMS registration with
  your Dutch SIM before building around it.

## Status / Roadmap

- [x] Research: model identification, prior art, modem options, ringer circuits
      ([RESEARCH.md](RESEARCH.md))
- [ ] Bench: measure bell coil resistance + resonant frequency (sweep ~18–30 Hz)
- [ ] Bench: identify dial faceplate (Dutch vs Swedish mapping), scope the pulse train
- [ ] Order: Ag1171 SLIC (Electrokit/DigiKey), A7670E board, BQ24074 breakout
- [ ] Bench: verify the Ag1171 (low-power ringer) rings the twin-gong bells convincingly
- [ ] Bench: test 24–28 V square-wave direct bell drive vs SLIC drive
- [ ] Verify VoLTE on A7670E with a Dutch carrier SIM (else switch to LARA-R6801)
- [ ] Power chain: USB-C → charger → 1S pack → rails, ride-through test under TX burst
- [ ] Handset interface: carbon mic bias + level matching to modem audio
- [ ] ESP32 firmware: pulse decode, hook state machine, AT call control, ring cadence
- [ ] Integration: fit everything in the bakelite case, antenna placement
- [ ] The first call ☎

## Prior art & references

- [Trasselfrisyr/SLIC-GSM-rotary-phone](https://github.com/Trasselfrisyr/SLIC-GSM-rotary-phone) — SLIC architecture reference (QCX601, rings real bells)
- [danjulio/weeBell_hardware](https://github.com/danjulio/weeBell_hardware) — ESP32 + **Ag1171** driving vintage phones (closest architecture to this build)
- [Ag1171 datasheet](https://silvertel.com/images/datasheets/Ag1171-datasheet-Low-cost-ringing-SLIC-with-single-supply.pdf) — Silvertel low-power ringing SLIC, single 3.3–5V supply
- [talofer99/Rotary_phone](https://github.com/talofer99/Rotary_phone) — ESP32 pulse-decode firmware reference
- [jonscheiding/phone-ringer](https://github.com/jonscheiding/phone-ringer) — boost + H-bridge + transformer ring generator (40–60 V AC)
- [Sky's Edge Rotary Un-Smartphone](https://skysedge.com/telecom/RUSP/index.html) — modern VoLTE-verified reference design
- [matilo.eu — type 1951](http://www.matilo.eu/3-the-phones/1945-1960-late-bakelietperiode/ericsson-type-1951-tafeltelefoon-met-aardtoets/?lang=en) — model history & restoration
- Full cited research: [RESEARCH.md](RESEARCH.md)
