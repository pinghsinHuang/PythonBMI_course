# BMI Gauge Display Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an accessible horizontal BMI range gauge with a pointer to the calculated result card.

**Architecture:** Reuse the rounded BMI value and existing category thresholds from Flask. Pass a clamped position on a 0–40 scale to the Jinja template, which renders a CSS-positioned pointer above four labeled range segments.

**Tech Stack:** Python 3.9, Flask/Jinja, CSS, unittest.

**Spec:** `docs/superpowers/specs/2026-11-02-bmi-gauge-design.md`

## Global Constraints

- Preserve the current BMI calculation, rounded display value, category thresholds (18.5, 24, 27), and advice.
- Add the gauge only to the calculated result card.
- Use the existing Flask/Jinja and CSS stack; add no JavaScript or dependencies.
- Keep the range and pointer readable on narrow screens and expose an accessible text description.

## Review Focus

- BMI rounds to 0.0: the pointer remains at the start of the scale. Test in `test_bmi_gauge_position_starts_at_zero`.
- BMI is exactly 18.5, 24, or 27: the pointer's category and existing classification agree. Existing threshold coverage is `test_taiwan_adult_thresholds`; add gauge assertions for rendered band labels.
- BMI is at the scale maximum of 40: the pointer reaches 100%. Test in `test_bmi_gauge_position_clamps_at_scale_maximum`.
- BMI exceeds 40: the pointer stays within the scale while the displayed BMI and category remain unchanged. Test in `test_bmi_gauge_position_clamps_above_scale_maximum`.
- Invalid form values: no gauge is rendered. Existing coverage is `test_invalid_fields_do_not_produce_result`.

---

### Task 1: Render the accessible BMI range gauge

**Files:**
- Modify: `app.py`
- Modify: `templates/index.html`
- Modify: `static/style.css`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `displayed_bmi` and the existing `bmi_guidance(displayed_bmi)` result.
- Produces: `result["gauge_position"]`, a finite percentage in `[0, 100]`, computed as `min(displayed_bmi, 40) / 40 * 100`.
- Template uses `gauge_position` for the pointer position and the existing `result.label` for the accessible current category.

- [x] **Step 1: Write failing tests** in `tests/test_app.py` for the rendered gauge at BMI 22.5 (position 56.25%), the four category labels, and its accessible description; add cases for BMI 0.0, 40.0, and values above 40 (including a very large finite value) to verify pointer clamping.

- [x] **Step 2: Run the tests and verify the expected failures**

Run: `./.venv-py39/bin/python -m unittest tests.test_app`
Expected: FAIL because the result page has no gauge or gauge position.

- [x] **Step 3: Add `gauge_position`** to the successful result data in `app.py`, clamping `displayed_bmi` to 40 before converting it to a percentage so large finite values cannot overflow.

- [x] **Step 4: Add the labeled four-band gauge** to the calculated result card in `templates/index.html`; position its pointer from `result.gauge_position` and include an accessible description containing the current category.

- [x] **Step 5: Style the gauge** in `static/style.css` with distinct segments for underweight, healthy, overweight, and obesity ranges; keep the pointer within the track and adapt the gauge to the existing narrow-screen layout.

- [x] **Step 6: Run the full test suite**

Run: `./.venv-py39/bin/python -m unittest discover -s tests`
Expected: all tests pass, including the existing classification, invalid-input, and escaping tests.

- [x] **Step 7: Check the patch**

Run: `git diff --check`
Expected: no whitespace errors.
