# MeetingHub-4

Analog audio hub for 4 laptops — monitor all four at once (per-source + master
volume), speak on one at a time with a physical mic selector, use one ordinary
TRRS headset, install nothing on any laptop. 100 % analog: no USB audio, no
Bluetooth, no firmware.

## Versions

| | [`v1/`](v1/) — fabricated | [`v2/`](v2/) — respin | [`v3/`](v3/) — mic selector only |
|---|---|---|---|
| Scope | monitor 4 + talk on 1 | monitor 4 + talk on 1 | **talk on 1 only** (audio → external mixer + Y-cables) |
| PCB | 4-layer, 265 × 160 mm | **2-layer**, 192 × 156 mm | **4-layer** (GND + 5 V planes), ~**106 × 86 mm** |
| Assembly | 3 SMD groups + jack SMD pads | **100 % through-hole** | **100 % through-hole** (vertical passives) |
| Mic selector | latching push-locks driving relays | **on-board one-hot latch** (CD4043B + diode matrix + 2N7000), momentary buttons, power-on = muted | **same one-hot latch**; relay NC pulled to GND via 2k2 so a de-selected notebook still reads "mic present" |
| Audio path | mixer + headphone amp + pots + VBIAS | mixer + headphone amp + pots + VBIAS (LM358) | **none** |
| Status | fabricated (JLCPCB lot `W2026080810364558`); first article found 3 schematic bugs | routed, DRC-clean; **not yet fabricated** | routed, DRC-clean, sim 22/22; **not yet fabricated** — open in KiCad, run native ERC/DRC first |

Each folder is **self-contained** (its own `hardware/`, `docs/`, scripts, BOM,
gerbers). Start with the `README.md` / `CLAUDE.md` inside the folder you want.

- **v1 history & rework:** `v1/README.md`, `v1/docs/REWORK-001…004`,
  `v1/docs/Architecture/SCH-010-OneHotMicSelector.md` (the selector design that
  became v2).
- **v2 design & build:** `v2/README.md`, `v2/docs/v2-DESIGN.md`,
  `v2/docs/v1-vs-v2.md`, `v2/CHANGELOG.md`.
- **v3 (mic selector only):** `v3/README.md`, `v3/docs/v3-DESIGN.md`,
  `v3/CHANGELOG.md`.

## License

Commercial license with usage royalty — see [LICENSE.md](LICENSE.md). Not open
hardware; commercial use requires a paid license. No document here is legal
advice.
