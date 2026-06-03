# NPS SO-3431 Public Comment Analysis

**Center for Western Priorities** · [westernpriorities.org](https://westernpriorities.org)

An analysis of 35,700 public comments submitted through QR codes posted at national parks under Interior Secretary Order 3431, which asked visitors to report signs that "disparage" American history.

**Finding:** Fewer than 1 in 800 comments (0.1%) actually flagged a sign for removal — the form's stated purpose. The overwhelming majority were used to defend historical accuracy, express support for the National Park Service, or push back against the administration's order.

→ [View the interactive visualization](#) *(update with published URL)*

---

## Files

| File | Description |
|---|---|
| `classify_nps_comments.py` | Full annotated Python classification script |
| `nps_so3431_cwp.html` | Self-contained interactive visualization |

---

## Data

The 35,700-row dataset was released May 22, 2026 by the Department of the Interior in response to a FOIA request filed by KOAA News 5. The full dataset is available directly from the [National Park Service FOIA site](https://www.nps.gov/aboutus/foia/upload/NPS_SO3431_QR_Comments-For-Release.xlsx).

To run the classifier:
```bash
pip install pandas openpyxl
python classify_nps_comments.py
```
Place `NPS_SO3431_QR_Comments-For-Release.xlsx` in the same directory first.

---

## Results summary

| Category | Count | % of total |
|---|---|---|
| General opposition to the order | 9,873 | 28% |
| Coordinated form letters (all opposition) | 13,308 | 37% |
| Defend historical accuracy | 5,272 | 15% |
| General pro-parks support | 4,236 | 12% |
| Park visit experience | 1,614 | 5% |
| Trump / Burgum criticism | 669 | 2% |
| Off-topic / jokes / spam | 660 | 2% |
| **Flagged signage or supported removal** | **47** | **0.1%** |

---

## Methodology summary

Comments were classified in two passes: (1) identification of coordinated template campaigns, and (2) rule-based keyword/phrase matching to assign original comments to seven categories. Classification was developed with the assistance of Claude AI and verified by CWP staff across six rounds of human review, achieving approximately 89% overall accuracy in the final round. The "flagged signage or supported removal" category was verified through a complete manual review of all AI-categorized entries.

See the methodology section of the visualization for full details.

---

*Analysis by the Center for Western Priorities · Developed with the assistance of Claude AI*
