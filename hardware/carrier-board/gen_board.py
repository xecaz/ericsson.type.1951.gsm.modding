#!/usr/bin/env python3
"""
Carrier / interconnect board generator for the Ericsson 1951 -> cellular build.

Ties together three off-the-shelf 2.54 mm-header modules and breaks out the phone's
own electromechanical parts onto clearly-marked terminals:
  - ESP32-DevKitC (38-pin, 2x19)             -- state machine / AT host
  - Waveshare A7670E Cat-1 HAT (2x20, SKU 20049) -- LTE Cat-1 / VoLTE modem
  - Silvertel Ag1171 SLIC (14-pin SIL)       -- ring generation
Phone terminals (large pads): BELL (ringer), MIC, SPK (handset), HOOK, DIAL.
On-board passives: C1 = Ag1171 supply decoupling, C2 = 5V bulk for modem TX bursts.

TALL-STRIP layout: modules stand VERTICAL, side by side -> board 44 x 100 mm,
inside a 45 x 120 mm mill bed. Single copper layer (B.Cu); GND is a bottom pour;
every net is copper EXCEPT PWRKEY (one silk-labelled through-hole WIRE JUMPER).

Run: python3 gen_board.py   -> writes carrier.kicad_pcb
"""
import pcbnew
from pcbnew import VECTOR2I, FromMM

PITCH = 2.54

# ---- CRITICAL FIT DIMENSION -------------------------------------------------
# Official Espressif ESP32-DevKitC = 25.4 mm (1.0") between header rows.
# MANY CLONES are 22.86 mm (0.9"). Modules solder onto rigid pins, so this MUST
# match your board. MEASURE WITH CALLIPERS, then set here and re-run.
ESP_ROW = 25.4
# ----------------------------------------------------------------------------

board = pcbnew.NewBoard("/dev/null")

_nets = {}
def net(name):
    if name not in _nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); _nets[name] = n
    return _nets[name]

def pth_pad(fp, number, x, y, netname=None, drill=1.0, size=1.6, rect=False):
    p = pcbnew.PAD(fp)
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetShape(pcbnew.PAD_SHAPE_RECT if rect else pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(VECTOR2I(FromMM(size), FromMM(size)))
    p.SetDrillSize(VECTOR2I(FromMM(drill), FromMM(drill)))
    p.SetLayerSet(p.PTHMask())
    p.SetPosition(VECTOR2I(FromMM(x), FromMM(y)))
    p.SetNumber(str(number))
    if netname: p.SetNet(net(netname))
    fp.Add(p); return p

def module(ref, x, y, value=""):
    fp = pcbnew.FOOTPRINT(board); fp.SetReference(ref)
    if value: fp.SetValue(value)
    board.Add(fp); fp.SetPosition(VECTOR2I(FromMM(x), FromMM(y)))
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    return fp

def silk(text, x, y, size=1.0, angle=0):
    t = pcbnew.PCB_TEXT(board); t.SetText(text); t.SetLayer(pcbnew.F_SilkS)
    t.SetPosition(VECTOR2I(FromMM(x), FromMM(y)))
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    if angle: t.SetTextAngle(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T))
    board.Add(t); return t

def track(netname, pts, width=0.6, layer=pcbnew.B_Cu):
    n = net(netname) if netname else None
    for a, b in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(VECTOR2I(FromMM(a[0]), FromMM(a[1])))
        t.SetEnd(VECTOR2I(FromMM(b[0]), FromMM(b[1])))
        t.SetWidth(FromMM(width)); t.SetLayer(layer)
        if n: t.SetNet(n)
        board.Add(t)

def edge(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(VECTOR2I(FromMM(x1), FromMM(y1)))
    s.SetEnd(VECTOR2I(FromMM(x2), FromMM(y2)))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.15)); board.Add(s)

def mount_hole(x, y, drill=3.2):
    fp = module("H", x, y)
    p = pcbnew.PAD(fp); p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(VECTOR2I(FromMM(drill), FromMM(drill)))
    p.SetDrillSize(VECTOR2I(FromMM(drill), FromMM(drill)))
    p.SetLayerSet(p.UnplatedHoleMask())
    p.SetPosition(VECTOR2I(FromMM(x), FromMM(y))); fp.Add(p)

# ============================================================================
# LAYOUT  (mm; origin top-left. X = width <=45, Y = length <=120)
# ============================================================================
BW, BH = 44.0, 100.0
for a,b,c,d in [(0,0,BW,0),(BW,0,BW,BH),(BW,BH,0,BH),(0,BH,0,0)]: edge(a,b,c,d)
for hx,hy in [(4,4),(BW-4,4),(4,BH-4),(BW-4,BH-4)]: mount_hole(hx,hy)

# ---- ESP32-DevKitC (2x19), vertical -----------------------------------------
ESP_COLA = 9.0; ESP_COLB = ESP_COLA + ESP_ROW; yE = 22.0
esp_colA = ["3V3","EN","GPIO36","GPIO39","GPIO34","GPIO35","GPIO32","GPIO33",
            "GPIO25","GPIO26","GPIO27","GPIO14","GPIO12","GND","GPIO13","GPIO9",
            "GPIO10","GPIO11","5V"]
esp_colB = ["GND","GPIO23","GPIO22","GPIO1","GPIO3","GPIO21","GND","GPIO19",
            "GPIO18","GPIO5","GPIO17","GPIO16","GPIO4","GPIO0","GPIO2","GPIO15",
            "GPIO8","GPIO7","GPIO6"]
esp_net = {"GPIO25":"FR","GPIO26":"RM","GPIO27":"SHK","GPIO17":"TX","GPIO16":"RX",
           "GPIO4":"PWRKEY","GPIO14":"HOOK","GPIO13":"DIAL","5V":"5V","GND":"GND"}
U1 = module("U1", ESP_COLA, yE, "ESP32-DevKitC"); espx = {}
for i,(na,nb) in enumerate(zip(esp_colA, esp_colB)):
    y = yE + i*PITCH
    pth_pad(U1, f"A{i+1}", ESP_COLA, y, esp_net.get(na))
    pth_pad(U1, f"B{i+1}", ESP_COLB, y, esp_net.get(nb))
    espx[na] = (ESP_COLA, y); espx[nb] = (ESP_COLB, y)

# ---- Ag1171 SLIC (14-pin SIL), vertical, left of colA -----------------------
AG_X = ESP_COLA - PITCH; yAg = yE + 6*PITCH        # pin3 F/R beside GPIO25
ag_names = ["RING","TIP","F/R","RM","SHK","NC","NC","NC","VIN","VOUT","NC",
            "GNDPWR","+VPWR","PD"]
ag_net = {"RING":"RING","TIP":"TIP","F/R":"FR","RM":"RM","SHK":"SHK",
          "GNDPWR":"GND","+VPWR":"SLICV"}
U2 = module("U2", AG_X, yAg, "Ag1171"); agx = {}
for k,name in enumerate(ag_names):
    y = yAg + k*PITCH; pth_pad(U2, k+1, AG_X, y, ag_net.get(name)); agx[name] = (AG_X, y)

# ---- Waveshare A7670E HAT (2x20), vertical, right of colB --------------------
HAT_ROWB = ESP_COLB + PITCH; HAT_ROWA = ESP_COLB + 2*PITCH; yH = yE + 7*PITCH
hat_use = {2:"5V",4:"5V",7:"PWRKEY",8:"TX",10:"RX",6:"GND",14:"GND",20:"GND",30:"GND",34:"GND"}
U3 = module("U3", HAT_ROWB, yH, "A7670E-HAT"); hatx = {}
for c in range(20):
    y = yH + c*PITCH; pe, po = 2*c+2, 2*c+1
    pth_pad(U3, pe, HAT_ROWB, y, hat_use.get(pe), rect=(pe==2))
    pth_pad(U3, po, HAT_ROWA, y, hat_use.get(po), rect=(po==1))
    hatx[pe] = (HAT_ROWB, y); hatx[po] = (HAT_ROWA, y)

# ---- PHONE transducer terminals (LARGE pads) along the top edge -------------
TY = 12.0; BIG = dict(size=2.4, drill=1.3)
def term(ref, x, num, netname, **kw):
    fp = module(ref, x, TY); pth_pad(fp, num, x, TY, netname, **kw); return (x, TY)
# BELL (ringer) -> Ag1171 TIP/RING.  TIP escapes LEFT of RING (clears the pad).
bT = term("BELL", 3.5, 1, "TIP",  **BIG); bR = term("BELL", 6.5, 2, "RING", **BIG)
# HOOK switch -> ESP32 GPIO14 (+ GND)
term("HOOK", 10.5, 1, "HOOK", **BIG);     term("HOOK", 13.5, 2, "GND", **BIG)
# DIAL pulse -> ESP32 GPIO13 (+ GND)
term("DIAL", 17.5, 1, "DIAL", **BIG);     term("DIAL", 20.5, 2, "GND", **BIG)
# MIC / SPK (handset) -> land here, wire to the modem audio (see README)
term("MIC", 24.5, 1, None, **BIG);        term("MIC", 27.5, 2, None, **BIG)
term("SPK", 31.5, 1, None, **BIG);        term("SPK", 34.5, 2, None, **BIG)
silk("BELL",2.6,9.0,0.9); silk("HOOK",10.0,9.0,0.9); silk("DIAL",17.0,9.0,0.9)
silk("MIC",24.5,9.0,0.9);  silk("SPK",31.5,9.0,0.9)

# ---- SLIC supply terminal + decoupling cap C1 (clear below the Ag1171 tail) --
J3 = module("J3", 4.0, 74.0, "SLIC_PWR")
pth_pad(J3, 1, 4.0, 74.0, "SLICV", size=1.9, drill=1.1, rect=True)
pth_pad(J3, 2, 6.54, 74.0, "GND",  size=1.9, drill=1.1)
C1 = module("C1", 4.0, 77.6, "100uF")   # Ag1171 +VPWR bulk/decoupling
pth_pad(C1, 1, 4.0,  77.6, "SLICV", size=1.8, drill=1.0)
pth_pad(C1, 2, 6.54, 77.6, "GND",   size=1.8, drill=1.0)
silk("SLIC PWR 3-5V", 8.0, 73.4, 0.85); silk("C1 100uF", 8.0, 77.0, 0.85)

# ---- Power in + 5V bulk cap C2 (bottom) -------------------------------------
J2 = module("J2", 9.0, 88.0, "PWR_IN")
pth_pad(J2, 1, 9.0,  88.0, "5V",  size=2.0, drill=1.2, rect=True)
pth_pad(J2, 2, 12.0, 88.0, "GND", size=2.0, drill=1.2)
C2 = module("C2", 9.0, 84.0, "1000uF")  # 5V reservoir for modem TX bursts
pth_pad(C2, 1, 9.0,  84.0, "5V",  size=1.8, drill=1.0)
pth_pad(C2, 2, 11.54,84.0, "GND", size=1.8, drill=1.0)
silk("PWR IN 5V GND", 14.5, 88.4, 0.9); silk("C2 1000uF", 14.5, 84.4, 0.85)

# ============================================================================
# ROUTING  (single layer B.Cu; GND = pour)
# ============================================================================
track("FR",  [agx["F/R"], espx["GPIO25"]]); track("RM", [agx["RM"], espx["GPIO26"]])
track("SHK", [agx["SHK"], espx["GPIO27"]])
track("TX",  [hatx[8],  espx["GPIO17"]]);   track("RX", [hatx[10], espx["GPIO16"]])
# BELL -> SLIC TIP/RING
track("RING", [bR, (bR[0], agx["RING"][1]), agx["RING"]])
track("TIP",  [bT, (bT[0], agx["TIP"][1]),  agx["TIP"]])
# HOOK/DIAL -> ESP32 GPIO (down the centre gap, then short hop onto colA)
track("HOOK", [(10.5,TY), (10.5, espx["GPIO14"][1]), espx["GPIO14"]])
track("DIAL", [(17.5,TY), (17.5, espx["GPIO13"][1]), espx["GPIO13"]])
# SLIC +VPWR: C1 -> terminal -> pin13 (all on X=4, then hop right; misses PD)
track("SLICV", [(4.0,77.6), (4.0, agx["+VPWR"][1]), agx["+VPWR"]])
# 5V: up into ESP32 5V pin, and a perimeter run to the HAT 5V pins
track("5V", [(9.0,88.0), espx["5V"]], width=0.8)
track("5V", [(9.0,88.0), (9.0,92.0), (41.0,92.0), (41.0,36.3),
             (HAT_ROWB,36.3), hatx[2], hatx[4]], width=0.8)

# PWRKEY = the one WIRE JUMPER (HAT pin7 -> ESP32 GPIO4)
silk("JMP", hatx[7][0]+1.0, hatx[7][1]-0.4, 0.9)
silk("PWRKEY", espx["GPIO4"][0]+1.2, espx["GPIO4"][1]+0.4, 0.9)

# ---- module names in the empty centre gap (X 11..32) ------------------------
silk("ESP32", 15.0, 26.0, 1.4); silk("DevKitC U1", 12.5, 29.0, 1.0)
silk("Ag1171 U2", 12.5, 42.0, 1.1)
silk("A7670E", 15.0, 57.0, 1.4); silk("HAT U3", 15.5, 60.0, 1.0)
silk("2x20 RPi", 13.5, 63.0, 0.9); silk("pin2 v", HAT_ROWB-1.0, yH-2.4, 0.85)

# ---- GND pour ---------------------------------------------------------------
z = pcbnew.ZONE(board); z.SetLayer(pcbnew.B_Cu); z.SetNet(net("GND"))
z.SetLocalClearance(FromMM(0.25)); z.SetMinThickness(FromMM(0.2))
z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
poly = pcbnew.SHAPE_POLY_SET(); poly.NewOutline()
for px,py in [(3.0,6.5),(38.5,6.5),(38.5,93.5),(3.0,93.5)]:
    poly.Append(FromMM(px), FromMM(py))
z.SetOutline(poly); board.Add(z); pcbnew.ZONE_FILLER(board).Fill(board.Zones())

# ---- titles (clear gap between the HAT label and the SLIC/C1 labels) --------
silk("Ericsson 1951", 13.0, 66.0, 1.0)
silk("4G-VoLTE carrier", 13.0, 69.0, 0.9)
silk("rev B 44x100 1jmp", 13.0, 72.0, 0.85)

out = "/home/xecaz/haxx/ericsson.type.1951/hardware/carrier-board/carrier.kicad_pcb"
pcbnew.SaveBoard(out, board)
print("saved", out, f"| board {BW}x{BH} mm | ESP_ROW={ESP_ROW}")
print("nets:", sorted(_nets.keys()))
