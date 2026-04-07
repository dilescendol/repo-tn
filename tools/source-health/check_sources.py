from __future__ import annotations

import json
import re
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "index.json"
README_PATH = ROOT / "README.md"
DOCS_DIR = ROOT / "docs"
STATUS_DOC_PATH = DOCS_DIR / "SOURCE_STATUS.md"

SECTION_START = "<!-- official-wave:start -->"
SECTION_END = "<!-- official-wave:end -->"

PROBE_URL_OVERRIDES = {
    "anichin-compat": "https://anichin.moe/anime/?order=update",
    "animasu-compat": "https://v1.animasu.app/anime-sedang-tayang-terbaru/",
    "animesail-compat": "https://154.26.137.28/rilisan-anime-terbaru/page/",
    "animexin-compat": "https://animexin.dev/anime/?order=update&status=&type=",
    "anixverse-compat": "https://anixverseone.com/anime/?order=update",
    "anoboy-compat": "https://ww1.anoboy.boo/",
    "donghub-compat": "https://donghub.vip/anime/?order=update",
    "hidoristream-compat": "https://v2.hidoristream.online/",
    "kuramanime-compat": "https://v17.kuramanime.ink/",
    "nontonanimeid-compat": "https://s11.nontonanimeid.boats/",
    "oploverz-compat": "https://anime.oploverz.ac/",
    "otakudesu-compat": "https://otakudesu.blog/ongoing-anime/page/1/",
    "oppadrama-compat": "http://45.11.57.129/series/?status=&type=&order=update",
    "pencurimovie-compat": "https://ww99.pencurimovie.bond/movies",
    "samehadaku-compat": "https://v2.samehadaku.how/",
    "winbu-compat": "https://winbu.net/film/",
}

BLOCKED_MARKERS = (
    "turnstile",
    "attention required",
    "verify you are human",
    "captcha",
    "cloudflare",
)

GUARDED_MARKERS = (
    "loading..",
    "_as_turnstile",
    "just a moment",
)

STATUS_ORDER = {
    "active": 0,
    "guarded": 1,
    "thin": 2,
    "blocked": 3,
    "slow": 4,
    "dead": 5,
    "error": 6,
}

STATUS_LABELS = {
    "active": "🟢 Active",
    "guarded": "🟡 Guarded",
    "thin": "🟠 Thin",
    "blocked": "🟠 Blocked",
    "slow": "🟠 Slow",
    "dead": "🔴 Dead",
    "error": "🔴 Error",
}


@dataclass
class ProbeResult:
    state: str
    note: str
    http_status: str
    final_url: str


def load_index() -> list[dict]:
    root = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return list(root.get("extensions", []))


def probe_url(url: str) -> ProbeResult:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; RepoTnSourceHealth/1.0; +https://github.com/dilescendol/repo-tn)",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        },
    )
    insecure_context = ssl.create_default_context()
    insecure_context.check_hostname = False
    insecure_context.verify_mode = ssl.CERT_NONE

    try:
        with urlopen(request, timeout=20, context=insecure_context) as response:
            status = str(getattr(response, "status", 200))
            body = response.read(160_000).decode("utf-8", errors="ignore").lower()
            final_url = response.geturl()
    except HTTPError as error:
        body = error.read(80_000).decode("utf-8", errors="ignore").lower()
        final_url = error.geturl()
        if error.code in (401, 403):
            return ProbeResult("blocked", "Upstream answered but access is restricted.", str(error.code), final_url)
        if error.code == 404:
            return ProbeResult("dead", "Probe URL returned 404.", str(error.code), final_url)
        return ProbeResult("error", f"HTTP {error.code} from upstream.", str(error.code), final_url)
    except URLError as error:
        return ProbeResult("dead", f"Network error: {error.reason}", "-", url)
    except TimeoutError:
        return ProbeResult("slow", "Probe timed out before the page responded.", "-", url)
    except Exception as error:  # pragma: no cover - defensive
        return ProbeResult("error", f"Probe failed: {error}", "-", url)

    if any(marker in body for marker in BLOCKED_MARKERS):
        return ProbeResult("guarded", "Upstream is behind a gate or anti-bot challenge.", status, final_url)
    if any(marker in body for marker in GUARDED_MARKERS):
        return ProbeResult("guarded", "Upstream responded with a guarded loading page.", status, final_url)
    if 200 <= int(status) < 400:
        if len(body.strip()) < 800:
            return ProbeResult("thin", "Upstream responded, but the HTML body was unusually small.", status, final_url)
        return ProbeResult("active", "Probe returned a normal HTML response.", status, final_url)
    return ProbeResult("error", f"Unexpected HTTP {status}.", status, final_url)


def classify_source(extension: dict) -> dict:
    source_id = extension.get("id", "").strip()
    probe_target = PROBE_URL_OVERRIDES.get(source_id, extension.get("upstreamUrl", "").strip())
    probe = probe_url(probe_target) if probe_target else ProbeResult("error", "Missing probe URL.", "-", "")
    return {
        "id": source_id,
        "name": extension.get("name", source_id),
        "status": probe.state,
        "status_label": STATUS_LABELS.get(probe.state, probe.state.title()),
        "http_status": probe.http_status,
        "probe_url": probe_target,
        "note": probe.note,
        "final_url": probe.final_url,
    }


def build_summary_counts(results: Iterable[dict]) -> dict[str, int]:
    results = list(results)
    return {
        "active": sum(1 for item in results if item["status"] == "active"),
        "guarded": sum(1 for item in results if item["status"] == "guarded"),
        "thin": sum(1 for item in results if item["status"] == "thin"),
        "dead": sum(1 for item in results if item["status"] in {"dead", "error"}),
    }


def sorted_results(results: Iterable[dict]) -> list[dict]:
    return sorted(results, key=lambda item: (STATUS_ORDER.get(item["status"], 99), item["name"].lower()))


def write_status_doc(results: list[dict], generated_at: str) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    counts = build_summary_counts(results)
    lines = [
        "# Source Web Status",
        "",
        f"_Generated automatically on {generated_at}_",
        "",
        f"- Active: **{counts['active']}**",
        f"- Guarded: **{counts['guarded']}**",
        f"- Thin/partial: **{counts['thin']}**",
        f"- Dead or error: **{counts['dead']}**",
        "",
        "| Source | Web status | HTTP | Probe URL | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in sorted_results(results):
        probe_link = f"[Open]({result['probe_url']})" if result["probe_url"] else "-"
        lines.append(
            f"| {result['name']} | {result['status_label']} | {result['http_status']} | {probe_link} | {result['note']} |"
        )
    STATUS_DOC_PATH.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def update_readme(results: list[dict], generated_at: str) -> None:
    counts = build_summary_counts(results)
    lines = [
        SECTION_START,
        f"_Auto-generated on {generated_at}_",
        "",
        "| Active | Guarded | Thin | Dead/Error |",
        "| --- | --- | --- | --- |",
        f"| **{counts['active']}** | **{counts['guarded']}** | **{counts['thin']}** | **{counts['dead']}** |",
        "",
        "| Source | Web status | HTTP | Probe |",
        "| --- | --- | --- | --- |",
    ]
    for result in sorted_results(results):
        probe_link = f"[Open]({result['probe_url']})" if result["probe_url"] else "-"
        lines.append(
            f"| {result['name']} | {result['status_label']} | {result['http_status']} | {probe_link} |"
        )
    lines.extend(
        [
            "",
            "Detail report: [`docs/SOURCE_STATUS.md`](docs/SOURCE_STATUS.md)",
            SECTION_END,
        ]
    )
    generated_section = "\n".join(lines)
    readme = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(rf"{re.escape(SECTION_START)}.*?{re.escape(SECTION_END)}", re.DOTALL)
    if pattern.search(readme):
        updated = pattern.sub(generated_section, readme)
    else:
        anchor = "## Current Official Wave"
        if anchor in readme:
            updated = readme.replace(anchor, anchor + "\n\n" + generated_section, 1)
        else:
            updated = readme.rstrip() + "\n\n" + generated_section + "\n"
    README_PATH.write_text(updated, encoding="utf-8")


def main() -> None:
    generated_at = datetime.now(timezone.utc).astimezone().strftime("%d %b %Y %H:%M %Z")
    results = [classify_source(extension) for extension in load_index()]
    write_status_doc(results, generated_at)
    update_readme(results, generated_at)
    print(f"Generated repo-tn source status for {len(results)} entries.")


if __name__ == "__main__":
    main()
