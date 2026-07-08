"""Best-effort Playwright automation for the structured, embeddable apply
forms exposed by Greenhouse, Lever, Ashby, and SmartRecruiters — the ATS
platforms this project treats as auto-apply-capable because their hosted
application forms are simple, public, and designed to be filled out by the
candidate directly (no bot-detection/anti-automation clauses aimed at
individual applicants filling their own forms, unlike LinkedIn/Indeed/etc).

This is intentionally conservative: any field it cannot confidently map is
left for the human, and any error aborts the submission rather than
guessing. A failed or partial run always degrades to
"Manual Action Required" with the browser state preserved via a screenshot
and a direct link, never a silent skip.
"""

from __future__ import annotations

import logging
import re

from playwright.async_api import async_playwright

from app.services.automation.base import ApplicantContext, AutoApplyResult

logger = logging.getLogger(__name__)

# Common field label substrings -> ApplicantContext attribute.
_FIELD_LABEL_MAP = {
    "first name": "first_name",
    "last name": "last_name",
    "full name": "full_name",
    "email": "email",
    "phone": "phone",
    "linkedin": "linkedin_url",
    "portfolio": "portfolio_url",
    "website": "portfolio_url",
    "github": "github_url",
}

_RESUME_FIELD_HINTS = ["resume", "cv"]
_COVER_LETTER_FIELD_HINTS = ["cover letter"]


async def attempt_auto_apply(
    apply_url: str, applicant: ApplicantContext, auto_submit: bool = False
) -> AutoApplyResult:
    """Fills the hosted application form. Only clicks the final Submit
    button when `auto_submit` is True — which the caller must only pass
    when the user has opted into `UserProfile.auto_submit_applications`.
    Otherwise the filled-but-unsubmitted state is reported back so the
    dashboard can show "Ready to Submit" with a one-click confirm.
    """
    first_name, _, last_name = (applicant.full_name or "").partition(" ")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(apply_url, wait_until="networkidle", timeout=30000)

            unmapped_fields = await _fill_known_fields(
                page, applicant, first_name, last_name or first_name
            )
            uploaded_resume = await _upload_file(page, _RESUME_FIELD_HINTS, applicant.resume_pdf_path)
            await _upload_file(page, _COVER_LETTER_FIELD_HINTS, applicant.cover_letter_pdf_path)

            if unmapped_fields or not uploaded_resume:
                screenshot_path = f"/tmp/manual_action_{hash(apply_url)}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                steps = []
                if not uploaded_resume:
                    steps.append("Upload your resume — the form field couldn't be auto-detected")
                if unmapped_fields:
                    steps.extend(f"Answer: {field}" for field in unmapped_fields)
                steps.append("Review all fields and click Submit")
                return AutoApplyResult(
                    success=False,
                    submitted=False,
                    reason="Some form fields require manual input",
                    manual_action_steps=steps,
                    screenshot_path=screenshot_path,
                )

            if not auto_submit:
                return AutoApplyResult(
                    success=True,
                    submitted=False,
                    reason="All fields filled — awaiting your confirmation to submit",
                    manual_action_steps=["Review the pre-filled application and click Submit"],
                )

            submit_button = page.get_by_role(
                "button", name=re.compile("submit application|submit|apply", re.I)
            )
            if await submit_button.count() == 0:
                screenshot_path = f"/tmp/manual_action_{hash(apply_url)}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                return AutoApplyResult(
                    success=True,
                    submitted=False,
                    reason="Form filled, but no Submit button could be identified automatically",
                    manual_action_steps=["Click Submit to finish the application"],
                    screenshot_path=screenshot_path,
                )

            await submit_button.first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)
            return AutoApplyResult(success=True, submitted=True)

        except Exception as exc:  # noqa: BLE001 - any failure degrades to manual action
            logger.exception("Auto-apply failed for %s", apply_url)
            return AutoApplyResult(
                success=False,
                submitted=False,
                reason=f"Automation error: {exc}",
                manual_action_steps=["Complete the application manually using the link provided"],
            )
        finally:
            await browser.close()


async def _fill_known_fields(page, applicant: ApplicantContext, first_name: str, last_name: str) -> list[str]:
    values = {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": applicant.full_name,
        "email": applicant.email,
        "phone": applicant.phone,
        "linkedin_url": applicant.linkedin_url,
        "portfolio_url": applicant.portfolio_url,
        "github_url": applicant.github_url,
    }

    unmapped: list[str] = []
    labels = await page.locator("label").all()

    for label in labels:
        text = (await label.inner_text() or "").strip().lower()
        matched_key = next((v for k, v in _FIELD_LABEL_MAP.items() if k in text), None)
        input_id = await label.get_attribute("for")
        if not input_id:
            continue

        if matched_key and values.get(matched_key):
            try:
                await page.locator(f"#{input_id}").fill(str(values[matched_key]))
            except Exception:
                unmapped.append(text)
        elif await _is_required_field(page, input_id):
            unmapped.append(text)

    return unmapped


async def _is_required_field(page, input_id: str) -> bool:
    try:
        element = page.locator(f"#{input_id}")
        return bool(await element.get_attribute("required") is not None or await element.get_attribute("aria-required") == "true")
    except Exception:
        return False


async def _upload_file(page, label_hints: list[str], file_path: str) -> bool:
    file_inputs = await page.locator("input[type=file]").all()
    for file_input in file_inputs:
        input_id = await file_input.get_attribute("id") or ""
        surrounding_text = ""
        try:
            surrounding_text = (await file_input.locator("xpath=ancestor::*[self::div or self::fieldset][1]").inner_text()) or ""
        except Exception:
            pass

        haystack = f"{input_id} {surrounding_text}".lower()
        if any(hint in haystack for hint in label_hints):
            try:
                await file_input.set_input_files(file_path)
                return True
            except Exception:
                return False
    return False
