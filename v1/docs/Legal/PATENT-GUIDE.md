# International Patent Registration Guide — MeetingHub-4

**Version: 0.1 — Educational document, not legal advice**

---

## Read this first: an honest patentability assessment

Before any procedure, it is important to realistically assess whether this project has a real chance of being granted a patent. Based on the technical documentation in this repository (ERS-001, HAD-001, SCH-001 to SCH-009, PCB-001):

MeetingHub-4 combines circuit blocks that are **well known and widely published** — an op-amp summing stage for audio mixing, relays for microphone signal switching, a headphone amplifier, passive TRRS interfaces, and USB-C power supply — assembled in a straightforward way to meet a specific need (managing audio for 4 laptops with a single headset).

For a **utility patent** to be granted, most patent systems worldwide (including the Brazilian system, via INPI, and the PCT system) require three cumulative criteria:

1. **Novelty** — the solution must not already exist, published or in use, anywhere in the world, before the filing date.
2. **Inventive step / non-obviousness** — the solution cannot be an obvious step for a person skilled in the art, starting from what is already known.
3. **Industrial applicability** — the solution must be industrially manufacturable/usable (this criterion, on its own, MeetingHub-4 meets without issue).

**The real risk here lies in criteria 1 and 2.** Op-amp summing circuits, relay switching, and TRRS interfaces are analog electronics techniques taught in any basic electronics course and used in commercial products for decades. A patent examination (or a prior-art search performed before filing) would very likely find prior art covering the individual elements and, possibly, the combination itself — multi-source audio mixers with relay-based microphone selection are not a novel concept in the professional/broadcast audio market.

**This does not mean there is nothing to protect** — it just means the most appropriate protection is probably not a utility patent. See the "Alternatives" section below before deciding to spend time and money on an international filing.

**Concrete recommendation**: before spending anything on filing, hire a **professional prior-art search** (patent search) performed by a registered industrial property agent. It costs a fraction of the price of an international filing and answers the central question based on real evidence, not on assumption — including my own, written here without access to patent databases.

---

## Protection alternatives better suited to this type of project

| Protection | What it covers | Relative cost | Already covered in this project? |
|---|---|---|---|
| **Trade secret** | The project file itself (schematic, PCB) kept confidential | Low (contractual clause) | Yes — clause 7 of [LICENSE.md](../../LICENSE.md) |
| **Copyright** | The schematic/PCB files as technical drawings, and the written documentation | Low/none (automatic protection in most countries; formal registration reinforces proof of authorship) | Automatic from creation; consider formal registration if commercializing internationally |
| **Trademark** | The commercial name of the product ("MeetingHub-4" or the real sales brand name) and/or logo | Medium, per country/class | Not done - evaluate before commercial launch |
| **Design patent** | The visual appearance of the enclosure/panel, if it has its own distinctive design | Medium | Not yet applicable - depends on the enclosure design, which is not part of this electronic hardware project |
| **Utility patent** | A new and non-obvious technical solution | High (see below) | Evaluate via prior-art search before deciding |

For most niche hardware products like this one, the combination of **trade secret (protecting the project files) + trademark (protecting the commercial name) + a well-drafted license agreement** offers faster and cheaper practical protection than pursuing a patent with a real risk of rejection.

---

## If you still decide to proceed with an international patent filing

### Overview of the PCT system (Patent Cooperation Treaty)

The standard path to seeking protection in multiple countries from a single initial filing is the **Patent Cooperation Treaty (PCT)**, administered by WIPO. It **does not grant an "international patent"** (that does not exist as a single legal concept) — it allows reserving priority and deferring country-by-country decisions while the merits are evaluated.

**Typical steps:**

1. **National priority filing** (optional, but common): initial filing in the applicant's home country (e.g., INPI in Brazil) to establish a priority date. From this point, you have **12 months** to decide whether to enter the PCT claiming that priority.
2. **PCT international filing**: a single application, in a single language, filed at a receiving office (e.g., INPI, or directly at WIPO), claiming priority from the national filing (if any).
3. **International search (International Search Report)**: a search authority (e.g., INPI, EPO, USPTO, depending on where the application was filed) issues a report indicating relevant prior art found — **this is where novelty/inventive-step problems tend to surface publicly for the first time**.
4. **International publication**: the application is published (made public) 18 months from the earliest priority date.
5. **International preliminary examination** (optional): a preliminary opinion on patentability, useful for deciding whether it is worth proceeding.
6. **National phase entry**: within **30-31 months** from the priority date (the deadline varies by country), the applicant decides in **which specific countries** to actually proceed with examination and eventual grant — each country then examines and decides independently, according to its own law. **This is the phase where most of the real cost occurs** (translation, local agents, country-by-country examination fees).

### Key deadlines (summary)

| Milestone | Deadline from priority date |
|---|---|
| PCT filing claiming national priority | up to 12 months |
| International publication | 18 months |
| National phase entry (varies by country, e.g., Europe ~31 months, USA ~30 months) | 30-31 months |

### Costs (order of magnitude, **not fixed figures** — they vary by office, number of countries, and exchange rate; consult an agent for a real quote)

- Priority national filing: low to moderate.
- PCT filing + international search: moderate (typically a few thousand dollars/euros).
- **National phase in each country** (mandatory translation + local agent + fees): this is the item that weighs the most — each chosen country can cost independently, and choosing 5-10 countries can multiply the total cost several times over relative to the initial PCT filing.
- Maintenance (annuities) in each granted country, for the entire term of validity.

### Who to contact

- A **registered Industrial Property Agent** (in Brazil, accredited with INPI) for the national filing and guidance on the PCT.
- A **patent attorney** with international practice, or a firm with correspondents in each target country, for the national phase.
- **WIPO** itself provides free educational material on the PCT system (search for "WIPO PCT applicant's guide" directly on the official WIPO website).

---

## Executive summary

1. **Do not file anything before a professional prior-art search.** The risk of rejection for lack of novelty/inventive step is real and concrete for this type of project.
2. **Consider whether trade secret + trademark solves the real business problem** (preventing direct copying, protecting the commercial name) better and more cheaply.
3. **If the search indicates a real chance**, the path is: national priority filing → PCT → national phase entry in the countries of real commercial interest (not every country in the world — choose where you intend to sell).
4. **This entire process must be conducted by a qualified patent agent/attorney.** This document is only a map of the territory, not a substitute for professional guidance.
