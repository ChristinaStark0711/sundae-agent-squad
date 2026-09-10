# QA checklist

Automated (from `scripts/qa_checks.py` → `work/qa_checks.json`):

- [ ] Video duration = voiceover duration + end card (± 1.0 s), and within the brief's length range.
- [ ] No black intervals longer than 0.3 s except the opening/closing fades.
- [ ] No silence in the voiceover track longer than 2.5 s except the end card.
- [ ] Integrated loudness between -18 and -14 LUFS; true peak ≤ -1.0 dBTP.
- [ ] Resolution and fps match the brief; `faststart` present; pixel format yuv420p.
- [ ] Every EDL segment's source file exists and the segment start times match the shot list (± 0.25 s).

Visual (from the contact sheet and stills):

- [ ] Picture matches voiceover meaning at every shot start.
- [ ] Cuts land on phrase boundaries; no cut in the middle of a word.
- [ ] Generated clips: no readable text, logos, signage, captions or watermarks.
- [ ] Generated clips: hands, faces, architecture and physics look right at contact-sheet size and at full size for hero shots.
- [ ] Generated clips match the real footage's color temperature, grain and camera feel.
- [ ] No shot under 1.5 s or over 7 s without a reason. No three generated shots in a row when real footage exists.
- [ ] Real footage is cropped without losing the subject; no visible letterbox unless intended.
- [ ] Logo watermark present where the brief asks, correct size, not cropped; end card held 3-4 s; logo proportions untouched.
- [ ] Brand background color on cards is close to the brief's hex.
- [ ] Must-show moments from the brief are in; must-avoid items are out.
- [ ] Nothing presents a generated person as a named or identifiable real person.

Verdict rules:

- Any failed automated check, any readable text or artifact in a generated clip, or any
  picture/voice mismatch → FAIL with a fix list.
- Taste issues alone → PASS with review notes.
