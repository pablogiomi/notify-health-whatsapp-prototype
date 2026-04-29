# Business Case: WhatsApp Reminders for Notify Health Nigeria

## 1. Overview and Purpose

This document summarises the cost and effectiveness case for replacing or
augmenting Notify Health's current SMS/voice reminder system with WhatsApp
messages delivered via the Meta Cloud API.

The primary question is whether WhatsApp can improve vaccination attendance
at a cost per disability-adjusted life year (DALY) averted that meets the
GiveWell cost-effectiveness bar (~$100/DALY). A secondary question is
whether audio or image message formats produce meaningfully better recall
than text messages at the same unit cost.

---

## 2. Current Notify Health Scale

| Metric | Value |
|---|---|
| Caregiver reach | 10,000–20,000 active caregivers |
| Geographic coverage | 2 states (Kogi and one additional) |
| Reminders sent in pilot | 42,000+ |
| Vaccination uplift observed | 12–24 percentage points |
| Cost-effectiveness (current) | ~$11,000 per death averted |
| Rough DALY estimate (current) | ~$290/DALY |
| vs GiveDirectly benchmark | ~5× more cost-effective than GiveDirectly |

The $290/DALY current estimate reflects pilot-scale overhead. The
messaging technology cost is a small fraction of total program cost;
overhead (staff, monitoring, training, data collection) dominates. As the
program scales, overhead per message falls and cost-effectiveness improves.

---

## 3. Nigeria EPI Vaccination Schedule

The Nigeria Expanded Programme on Immunisation (EPI) specifies 7 contact
points across the first 12 months of life:

| Visit | Timing | Vaccines |
|---|---|---|
| 1 | Birth | BCG, OPV₀ |
| 2 | 6 weeks | OPV₁, Penta₁, PCV₁, Rota₁ |
| 3 | 10 weeks | OPV₂, Penta₂, PCV₂, Rota₂ |
| 4 | 14 weeks | OPV₃, Penta₃, PCV₃, IPV |
| 5 | 6 months | Vitamin A |
| 6 | 9 months | Measles, Yellow Fever, MenA |
| 7 | 12 months | Measles booster |

**R21 malaria vaccine:** Nigeria is in the phased rollout of the R21/Matrix-M
malaria vaccine (WHO-recommended 2023, pilot deployment ongoing in high-burden
states). This will add additional contact points. Kogi State, with high
malaria burden, is a likely inclusion candidate. This further increases the
value of maintaining caregiver engagement across the full first year.

Each campaign reminder maps to one EPI contact point, making the total per-
caregiver message volume 7 per child per EPI cycle (plus any R21 additions).

---

## 4. WhatsApp Penetration in Nigeria

| Population segment | WhatsApp penetration |
|---|---|
| Nigerian internet users | ~95% |
| All Nigerian mobile subscribers | ~45% |
| Conservative estimate, Kogi State | 30–40% |

Nigeria has approximately 100 million internet users (mid-2025). WhatsApp is
the dominant messaging platform — it is effectively the default for informal
communication. However, Kogi State is semi-rural and has lower connectivity
than Lagos or Abuja. A 30–40% reach estimate for Notify Health's target
caregiver population is therefore appropriate for planning.

**Implication:** WhatsApp cannot replace SMS for the full caregiver list.
It should be treated as an additional or complementary channel, with SMS
retained as fallback for caregivers not reachable on WhatsApp.

---

## 5. Channel Cost Comparison

All costs are per message or per call in Nigeria as of April 2026.
Exchange rate basis: USD/NGN ≈ 1,600.

| Channel | Per-message cost | Notes |
|---|---|---|
| SMS — Africa's Talking | ~$0.0015 | ₦2.50/message |
| SMS — Telerivet platform | ~$0.0070 | Per-message platform fee |
| **SMS total (AT + Telerivet)** | **~$0.0085** | |
| Voice — Africa's Talking | ~$0.0090 | ₦15/min; avg reminder ~1 min |
| Voice — Telerivet platform | ~$0.0070 | Per-call platform fee |
| **Voice total (AT + Telerivet)** | **~$0.016** | |
| **WhatsApp — Meta Cloud API direct** | **$0.014** | Nigeria utility rate card; no BSP markup |

WhatsApp is approximately 65% more expensive per message than the current
SMS setup, and roughly comparable to voice. However, the cost gap narrows
when adjusting for engagement: WhatsApp messages include read receipts,
audio/image support, and opt-out handling — none of which are standard in
the SMS + Telerivet setup.

**Why "direct API":** Using a WhatsApp Business Solution Provider (BSP)
typically adds $0.003–$0.010 per message in markup on top of Meta's rate.
Calling the Meta Cloud API directly eliminates this. The Notify Health
WhatsApp prototype uses the direct API; no BSP is involved.

---

## 6. Media Type Pricing

**Key finding: all media types cost the same per message under Meta's
Utility category pricing.**

| Media type | Meta cost/msg | Approx. data usage | Template complexity |
|---|---|---|---|
| Text | $0.014 | < 2 KB | Simple copy, fast approval |
| Audio | $0.014 | 50–200 KB | Requires audio file upload; file pre-uploaded to Meta |
| Image | $0.014 | 50–150 KB | Requires image file upload; image URL or handle |
| Video | $0.014 | 1–10 MB | Large download; unsuitable for low-bandwidth users |

Because text, audio, and image carry identical Meta costs, the choice of
media type is a pure question of effectiveness — not budget. This makes a
rigorous A/B test feasible: all arms cost the same per delivery attempt.

**Data usage matters for recipients on metered connections.** Text is
negligible. Audio (a 30-second reminder) uses ~100 KB. Image (e.g., a
vaccination schedule card) uses ~80 KB. Video is not recommended for
this population given data costs and connectivity constraints.

**Template approval:** All WhatsApp messages must use a pre-approved
Meta template. Text templates are approved within 24–72 hours. Audio
and image templates require uploading the media file at the time of
submission and may take slightly longer. One template per language must
be submitted; multi-language campaigns require separate submissions.

---

## 7. A/B Test Design

Three arms, equal cost per delivery attempt:

| Arm | Media | What recipient receives | Primary metric |
|---|---|---|---|
| A | Text | Written reminder with child name, vaccine, date | Appointment attendance |
| B | Audio | 30-second voice recording of the reminder | Play rate + attendance |
| C | Image | Vaccination schedule card with appointment circled | Image view rate + attendance |

**Secondary metrics (all arms):**
- WhatsApp delivery rate (delivered vs sent)
- Read/viewed status (from Meta webhook — note: audio "read" = played)
- Opt-out rate (STOP replies)
- Appointment attendance (requires linkage with Notify Health outcome data)
- Vaccination card scan rate (if cards are digitised)

**Hypothesis:** Audio messages increase recall in low-literacy populations.
Meta reports a `read` status for audio messages when the file is played —
this gives a direct proxy for engagement not available with text.

**Randomisation:** Randomise at the caregiver level, not the message level.
Each caregiver is assigned one arm for the duration of the pilot; switching
arms between contact points confounds the measurement.

**Minimum detectable effect:** With 5,000 caregivers per arm, a baseline
attendance rate of 60%, and a two-sided alpha of 0.05, the test can detect
a 5 percentage-point difference with ~80% power. With 3,000 per arm it
can detect ~7pp.

---

## 8. $/DALY Cost-Effectiveness Model

### Framework

```
program_cost  = caregivers × reminders × msg_cost × overhead_multiplier
dalys_averted = caregivers × uplift    × 0.027     × 38

cost_per_daly = program_cost / dalys_averted
```

**Parameters:**
- `reminders` = 7 (EPI contact points per child per year)
- `msg_cost` = $0.014 (Meta Cloud API, Nigeria, utility category)
- `0.027` = probability of death from vaccine-preventable disease per
  unvaccinated child (Nigeria U5 mortality ~75/1000; ~35% VPD-attributable)
- `38` = DALYs per death averted (child dying at age 2 in Nigeria, life
  expectancy ~63, adjusted for disability weights)
- `overhead_multiplier` = ratio of total program cost to messaging cost alone.
  At pilot scale this is very high (200–400×) because fixed staff costs
  dominate. At full scale (100k+ caregivers) it falls toward 50–100×.
- `uplift` = percentage-point increase in vaccination attendance attributable
  to the reminder

### Current pilot estimate

| Input | Value |
|---|---|
| Caregivers | 5,000 |
| Uplift | 15pp |
| Overhead multiplier | ~290× |
| **$/DALY** | **~$184** |

This is directionally consistent with the $290/DALY rough estimate (the
difference reflects uncertainty in overhead and uplift assumptions).

### Optimised scenario (scale + audio uplift)

| Input | Value |
|---|---|
| Caregivers | 20,000 |
| Uplift | 20pp (audio channel uplift hypothesis) |
| Overhead multiplier | 100× (scale efficiency) |
| **$/DALY** | **~$48** |

At this scenario the programme meets the GiveWell bar (~$100/DALY) by a
2× margin. Overhead reduction through scale is the dominant lever.

### Sensitivity table (caregivers = 15,000, fixed)

$/DALY by uplift and overhead multiplier. Cells meeting the $100/DALY
GiveWell bar are marked ✓.

| Overhead | 5pp | 10pp | 15pp | 20pp | 25pp |
|---|---|---|---|---|---|
| 50× | $96 ✓ | $48 ✓ | $32 ✓ | $24 ✓ | $19 ✓ |
| 100× | $191 | $96 ✓ | $64 ✓ | $48 ✓ | $38 ✓ |
| 150× | $287 | $143 | $96 ✓ | $72 ✓ | $57 ✓ |
| 200× | $382 | $191 | $127 | $96 ✓ | $76 ✓ |
| 300× | $573 | $287 | $191 | $143 | $115 |

The critical insight: **overhead multiplier is the primary lever**. Even
with a modest 15pp uplift, the programme becomes highly cost-effective if
overhead can be driven below 150×. Scale (more caregivers, same fixed cost)
is the most tractable path to achieving this.

---

## 9. Strategic Recommendations

1. **Use Meta Cloud API direct** — avoid BSP markup. The direct API saves
   $0.003–$0.010/message, which at 100k messages/year is $300–$1,000/year.
   At scale it becomes significant.

2. **Classify reminders as Utility, not Marketing** — Utility templates
   cost $0.014/message in Nigeria. Marketing templates cost more and face
   stricter user controls. Vaccination reminders with explicit opt-in
   consent qualify as Utility.

3. **Run the A/B test (text vs audio vs image)** — the incremental cost is
   zero. The potential uplift from audio (5–10pp vs text) translates directly
   into $/DALY improvement. This is the highest-value experiment Notify Health
   can run.

4. **Apply to Meta Social Impact programme** — non-profits doing public health
   work may qualify for discounted or subsidised messaging rates. Contact
   Meta's Social Impact team. Eligibility criteria include 501(c)(3) status
   or equivalent, verifiable public health mission, and documented reach.

5. **Model overhead reduction as the primary $/DALY driver** — the messaging
   cost is already low. Investment in operational efficiency (automation,
   training, community health worker productivity tools) will move the
   $/DALY needle more than any technology cost reduction.

---

## 10. Key Assumptions and What to Validate

| Assumption | Basis | How to validate |
|---|---|---|
| 30–40% WhatsApp reach in Kogi State | National penetration downscaled for rural area | Pre-campaign survey of caregiver phone usage |
| 15–20pp vaccination uplift from reminders | Notify Health pilot data | RCT or before/after comparison at new sites |
| Overhead multiplier of 100–200× at scale | Extrapolated from pilot cost data | Full program cost accounting at 20k caregiver scale |
| 0.027 VPD mortality rate | Nigeria U5 mortality statistics | Kogi State-specific HMIS data |
| $0.014/msg Meta rate stable | April 2026 rate card | Monitor Meta pricing quarterly — utility rates have changed historically |
| Audio uplift hypothesis | Plausible, not proven | A/B test (see section 7) |
| R21 malaria vaccine adds additional contact points | WHO rollout plan | Confirm Kogi State inclusion with NPHCDA |

---

## 11. Sources

- Meta Cloud API pricing: business.whatsapp.com/products/platform-pricing
  (Nigeria, Utility category, April 2026)
- Africa's Talking SMS pricing: africastalking.com/sms (Nigeria, April 2026)
- Africa's Talking Voice pricing: africastalking.com/voice (Nigeria, April 2026)
- Telerivet pricing: telerivet.com/pricing
- Nigeria internet and WhatsApp penetration: Statista Digital Economy
  Compass 2024; DataReportal Nigeria Digital 2025 report
- Nigeria EPI schedule: NPHCDA Routine Immunisation Schedule 2023;
  WHO Nigeria country office
- R21 malaria vaccine: WHO recommendation Oct 2023; NPHCDA rollout update 2024
- GiveWell cost-effectiveness bar: givewell.org/how-we-work/criteria
  (updated 2024; ~$100/DALY equivalent to 10× GiveDirectly)
- GiveDirectly cost-effectiveness: givewell.org/charities/give-directly
- Nigeria under-5 mortality: UNICEF Nigeria country data 2024;
  Nigeria NDHS 2021
- DALY weights: Global Burden of Disease 2021 study (IHME)
- Notify Health pilot data: internal program reports (Kogi State, 2023–2025)
