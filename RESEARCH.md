# Ericsson type 1951 → Cellular Conversion — Research Report

*Deep-research run 2026-06-06 — 21 sources, 88 claims extracted, 24 verified (3-0 adversarial votes unless noted).*

## 1. The phone itself

**Identity (verified 3-0):** "Ericsson type 1951" is the official **Dutch PTT designation**, not Swedish.
It's a fully bakelite desk phone that Ericsson Holland derived from the Swedish **Ericsson DBH15 (1947)**,
built to the Dutch **"Norm 51"** standard and manufactured in **Rijen, Noord-Brabant**.

- Primary collector source: [matilo.eu — Ericsson type 1951](http://www.matilo.eu/3-the-phones/1945-1960-late-bakelietperiode/ericsson-type-1951-tafeltelefoon-met-aardtoets/?lang=en)
- Restoration guide: [matilo.eu — Restauratie van een Ericsson type 1951](http://www.matilo.eu/restauratie/restauratie-van-een-ericsson-type-1951/?lang=en)
- Corroboration: dutchtelephones.com, telefoonmuseum.eu
- Wiring diagram hunting grounds: [telephonecollectors.info diagrams](https://www.telephonecollectors.info/index.php/browse/wiring-diagrams)

**Handset (verified 3-0):** carbon microphone (electromechanical). Early units have the older Ericsson
handset; later units an F1-style handset with capsules interchangeable across Norm 51 phones
(Ericsson capsule 15074, ~100 Ω PTT). The carbon mic *can* be kept but needs a DC bias path
(a few mA through the element); alternative is an electret swap + bias. Either way an interface
circuit between handset and modem audio jack is required.

**Dial (verified 3-0):** bakelite rotary dial, friction-brake governor — **do NOT oil the governor**
(ruins pulse timing). Leaf-spring contacts cleaned by drawing paper through them. Pulses are generated
on the return rotation by interrupting DC loop current at **~10 PPS nominal** (exchanges accepted 9–13 PPS).
Decoding spec: count breaks, ~100 ms/pulse period, ~60/40 break/make, inter-digit gap ≥ ~200–300 ms.

**⚠ Swedish dial trap (verified 3-0):** Swedish-numbered dials use an **inverted mapping**:
1 pulse = digit 0 … 10 pulses = digit 9. Dutch PTT dials most likely use the standard mapping
(10 pulses = 0), but since the design lineage is Swedish, **verify the actual faceplate on the unit**
before hardcoding `digit = pulses % 10`.

**Update (2026-06-06):** the builder's unit is believed to be a **Swedish- or Finnish-market DBH15**,
not the Dutch type 1951 derivative. Follow-up verification ([Wikipedia: Rotary dial](https://en.wikipedia.org/wiki/Rotary_dial),
[Pulse dialing](https://en.wikipedia.org/wiki/Pulse_dialing)): **Finland kept the standard mapping**
(1 pulse = 1 … 10 pulses = 0) despite using Swedish-made phones; only **Sweden** is inverted.
Identification: faceplate with **0 in the first hole** (shortest rotation) = Swedish inverted;
**0 in the last hole** = Finnish/standard. Swedish Televerket units are often marked "RIKSTELEFON".
Electrical specs (10 PPS, ~25 Hz ring, carbon mic) are identical across all three markets — only
the firmware digit map differs.

**Not found:** an original Ericsson/PTT service manual with exact bell-coil impedance, ringing voltage
rating, or capsule electrical specs. → Measure on the bench (see Open Questions).

## 2. Cellular for the Netherlands (2026)

2G/3G status (from telecompaper / datacenterdynamics reporting):

| Carrier | 2G | 3G |
|---|---|---|
| Odido | **shut down 2023** | gone |
| VodafoneZiggo | until end-**2026** | gone |
| KPN | extended to **Dec 2027** | gone |

→ Any SIM800/SIM900 (2G) build is a dead end. 3G fallback is worthless in NL. **VoLTE over LTE is the
only durable voice path.** Dutch LTE runs on B20/B8/B3/B1/B7.

**Module path A — SIMCom A7670E (cheap, band-correct, audio-ready):**
LTE Cat-1, FDD B1/B3/B5/B7/B8/B20 ("E" = Europe variant). The
[Waveshare A7670E Cat-1 HAT](https://www.waveshare.com/wiki/A7670E_Cat-1_HAT) has an
**onboard 3.5 mm audio jack** for calls; supports voice + SMS. Also the
[LilyGO T-SIM-A7670E](https://lilygo.cc/products/t-sim-a7670e) (note: the verification pass *refuted*
the claim that the T-A7670E R2 integrates the ESP32 specs as listed — check current board revision
specs yourself before buying).
**⚠ Risk:** documented VoLTE failures on A7670E (LilyGO GitHub issue #240 "A7670E Can't make VoLTE
calls"). VoLTE depends on carrier IMS provisioning/APN config. **Not verified working on a Dutch
carrier.** Test before committing, or buy from a returnable EU source.

**Module path B — u-blox LARA-R6801 (VoLTE-confirmed, pricier):**
What Sky's Edge ships in the [Rotary Un-Smartphone](https://skysedge.com/telecom/RUSP/index.html).
Datasheet-confirmed VoLTE (UBX-21004391); R6801 = EMEA variant, correct for NL. Harder to source as
a hobbyist module, but de-risks the entire voice path.

**SIM:** any Dutch prepaid/postpaid SIM with VoLTE enabled; some MVNOs don't provision IMS for
non-whitelisted IMEIs — prefer a main carrier SIM for first bring-up.

## 3. Build routes

| Route | Stack | Ring | Status |
|---|---|---|---|
| **Kit:** Sky's Edge Rotary Un-Smartphone | LARA-R6801 | own electronics | VoLTE-verified reference, but built for their enclosure, not a drop-in for the 1951 |
| **DIY C:** [SLIC-GSM-rotary-phone](https://github.com/Trasselfrisyr/SLIC-GSM-rotary-phone) (Trasselfrisyr) + [hackaday.io #18871](https://hackaday.io/project/18871/instructions) | Arduino + **QCX601 SLIC** + SIM800 | **real bells via SLIC** | architecture gold, modem obsolete — swap SIM800 → A7670E |
| **DIY D:** [talofer99/Rotary_phone](https://github.com/talofer99/Rotary_phone) | ESP32 + SIM800 | MP3 over I2S (not real bells) | best ESP32 pulse-decode firmware reference |
| **Ringer ref E:** [jonscheiding/phone-ringer](https://github.com/jonscheiding/phone-ringer) | MCU + LM2577 boost + L293D + 1:5 transformer | real bells, 40–60 V AC achieved | proven boost+H-bridge+transformer topology |
| Also seen | [smith1401/PartyPhone](https://github.com/smith1401/PartyPhone) | — | additional ESP32 prior art |

**Recommended route (synthesis):** hybrid DIY —
**ESP32 + A7670E (Waveshare HAT or LilyGO board) + SLIC front-end**, with LARA-R6801 as
fallback if A7670E VoLTE fails on your carrier.

**Sourcing update (2026-06-07):** the QCX601 is effectively unobtainable. Replacement:
**Silvertel Ag1171** — same SLIC concept, single 3.3–5V supply with integrated DC/DC + ring
generator (no 12 V boost rail needed), 14-pin SIL module. In stock at
[DigiKey](https://www.digikey.com/en/products/detail/silvertel/AG1171/21187236),
[Newark](https://www.newark.com/silvertel/ag1171-s/subscriber-line-interface-circuit/dp/08AM1737),
[Electrokit (SE)](https://www.electrokit.com/en/slic-subscriber-line-interface-600ohm-line).
[Datasheet](https://silvertel.com/images/datasheets/Ag1171-datasheet-Low-cost-ringing-SLIC-with-single-supply.pdf).
Prior art: [danjulio/weeBell_hardware](https://github.com/danjulio/weeBell_hardware) (ESP32 + Ag1171
ringing vintage phones). Caveat: Ag1171 is a *low-power* ringer (short-loop, ~470 Ω design target);
bench-verify it rings the high-impedance twin-gong bells — fallback is the boost + H-bridge route E.
Alternative zero-SLIC route: dial/hook contacts straight to GPIOs, resistor bias for the carbon mic,
boost + H-bridge for the bells.

The SLIC is the keystone: one IC gives you
- ~25 Hz ring generation driving the **original bells** over tip/ring (RC pin: ~1.2 s on / ~6 s off cadence, Hz pin: 25 Hz),
- hook-switch state on its SHK output,
- rotary pulse counting on the same SHK line,
- a proper loop current for the dial *and* a bias path for the carbon mic.

Handset audio goes to the modem's audio jack (A7670E HAT has one onboard).

## 4. Ringer — the iconic ring

- EU ringing standard: ~25 Hz (not US 20 Hz), 40–90 V AC. Telcordia GR-909 minimum 40 Vrms;
  UK practice 40–70 V at 25 Hz.
- Proven DIY result: boost (LM2577 → ~18 V) + H-bridge (L293D) + 1:5 step-up transformer
  → **40–60 V AC measured**, rings electromechanical bells (jonscheiding/phone-ringer; verified 3-0).
- SLIC route generates ring voltage internally — simplest authentic path.
- **Open question:** direct 24–28 V square-wave H-bridge drive at the bell's resonant frequency is
  *plausible but undocumented* — bench-test against the actual 1951 bells. Measure resonance by
  sweeping ~18–30 Hz.
- No source documented the 1951's exact bell coil impedance → measure DC resistance and ring current
  on the bench before sizing the drive.

## 5. Power (LiPo + USB-C)

**Verified recommendation:** single-cell Li-ion (parallel 18650s fine) + **TI BQ24074** power-path
charger (1.5 A, [datasheet](https://www.ti.com/lit/ds/symlink/bq24074.pdf)). DPPM (dynamic power-path
management) powers the system while charging and throttles charge current — exactly what keeps the
modem alive through 1–2 A LTE transmit bursts while plugged in.

- USB-C input: 5.1 kΩ pull-downs on CC1/CC2 required for C-to-C cable compatibility (user has modules with CC resistors — verify 5.1 kΩ pull-down config).
- Bulk reservoir ≥1000 µF + ceramics at the modem VBAT pins for TX spikes.
- Rails: battery → modem VBAT direct (3.4–4.2 V); buck/LDO → 3.3 V ESP32; Ag1171 SLIC runs directly from 3.3–5 V (integrated DC/DC + ring generator — no separate boost rail) — single-cell topology, no multi-cell complexity.
- User parts on hand: USB-C modules w/ CC resistors ✅, 18650s + boxes ✅, bucks ✅, 1S/2S/3S BMS (to check). To order: BQ24074 board (or use existing 1S charger initially), Ag1171 SLIC module (DigiKey/Newark/Electrokit), modem board.

## 6. Caveats & open questions

**Caveats**
- Phone-specific facts rest on specialist collector sites (matilo.eu, dutchtelephones.com) + museum corroboration; no primary PTT/Ericsson service manual found.
- Ring-generator results are US/20 Hz-centric hacker projects; retune for 25 Hz and your bells' resonance.
- A7670E VoLTE on Dutch carriers unverified — the single biggest project risk.
- One refuted claim: LilyGO T-A7670E R2 board spec listing (1-2 vote) — verify board specs at purchase time.

**Open questions (bench/next steps)**
1. Measure: bell coil DC resistance & impedance, ring current, resonant frequency; carbon capsule resistance.
2. Verify VoLTE on A7670E with a KPN/Odido/VodafoneZiggo SIM (AT+CSDVC / IMS registration) — or go LARA-R6801.
3. Check the dial faceplate: Dutch (standard) vs Swedish (inverted) digit mapping; verify with a scope/logic analyzer while dialing "0".
4. Test 24–28 V square-wave direct bell drive at resonance vs SLIC/transformer 40–60 V drive.

## Key sources

- matilo.eu type 1951 pages (model + restoration) — primary collector reference
- https://skysedge.com/telecom/RUSP/index.html — VoLTE-verified modern reference design
- https://github.com/Trasselfrisyr/SLIC-GSM-rotary-phone + https://hackaday.io/project/18871/instructions — QCX601 SLIC architecture
- https://github.com/talofer99/Rotary_phone — ESP32 pulse-decode firmware (INDIALPIN/PULSEPIN, 10 ms debounce, 10 pulses → 0)
- https://github.com/jonscheiding/phone-ringer — boost+H-bridge+transformer ring generator (40–60 V AC achieved)
- https://www.waveshare.com/wiki/A7670E_Cat-1_HAT — A7670E HAT with audio jack
- https://www.ti.com/lit/ds/symlink/bq24074.pdf — BQ24074 power-path charger
- 2G sunset: datacenterdynamics (KPN → Dec 2027), telecompaper (NL 2G end by ~2029 framing, VfZiggo end-2026, Odido done 2023)
