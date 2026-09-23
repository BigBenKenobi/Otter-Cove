from __future__ import annotations

import colorsys
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .protected_paths import ProtectedTargetError, validate_export_target

THEME_BUNDLE_VERSION = 1
HARMONY_MODES = ("Complementary", "Analogous", "Triadic", "Split Complementary")
APPEARANCE_MODES = ("Light", "Dark")
DENSITIES = ("Compact", "Comfortable", "Roomy")
TEXT_SIZES = ("Small", "Default", "Large")
FONT_KINDS = ("Monospace", "Sans Serif", "Serif")
KNOWN_EFFECTS = (
    "Solid", "Dots", "Synapse", "Rain", "Constellations",
    "Perlin Flow", "Petals", "Sparkles", "Embers", "Leaves",
)

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class ThemeBundleError(ValueError):
    """Raised when a saved/imported theme bundle is invalid."""


def normalize_hex_color(value: str) -> str:
    value = str(value).strip()
    if not _HEX_RE.fullmatch(value):
        raise ThemeBundleError(f"Invalid color: {value!r}")
    return value.lower()


def _rgb01(value: str) -> tuple[float, float, float]:
    value = normalize_hex_color(value)
    return tuple(int(value[i : i + 2], 16) / 255.0 for i in (1, 3, 5))  # type: ignore[return-value]


def _hex(rgb: tuple[float, float, float]) -> str:
    parts = [max(0, min(255, round(channel * 255))) for channel in rgb]
    return "#" + "".join(f"{part:02x}" for part in parts)


def _hsv_color(h: float, s: float, v: float) -> str:
    return _hex(colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v))))


def generate_harmony(accent: str, harmony: str, appearance: str) -> tuple[str, str, str, str, str]:
    """Return a deterministic five-color semantic preview.

    The output order is background, panel, accent, border, muted. The exact input
    accent is always the middle color so the preview cannot silently substitute a
    different accent. Neutral/greyscale accents intentionally stay neutral.
    """

    accent = normalize_hex_color(accent)
    if harmony not in HARMONY_MODES:
        raise ThemeBundleError(f"Unsupported harmony: {harmony!r}")
    if appearance not in APPEARANCE_MODES:
        raise ThemeBundleError(f"Unsupported appearance mode: {appearance!r}")

    red, green, blue = _rgb01(accent)
    hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
    if saturation < 1e-6:
        hue = 0.0

    offsets = {
        "Complementary": (0.0, 0.5),
        "Analogous": (-0.075, 0.075),
        "Triadic": (1.0 / 3.0, 2.0 / 3.0),
        "Split Complementary": (0.42, 0.58),
    }[harmony]

    # A neutral accent stays neutral. Otherwise backgrounds/panels are deliberately
    # subdued while border/muted colors show the selected harmony relationship.
    base_sat = 0.0 if saturation < 1e-6 else max(0.08, saturation * 0.28)
    relation_sat = 0.0 if saturation < 1e-6 else max(0.16, saturation * 0.62)

    if appearance == "Dark":
        background = _hsv_color(hue, base_sat, 0.13)
        panel = _hsv_color(hue, base_sat * 0.9, 0.19)
        border = _hsv_color(hue + offsets[0], relation_sat, 0.40)
        muted = _hsv_color(hue + offsets[1], relation_sat * 0.78, 0.62)
    else:
        background = _hsv_color(hue, base_sat * 0.50, 0.97)
        panel = _hsv_color(hue, base_sat * 0.25, 1.0)
        border = _hsv_color(hue + offsets[0], relation_sat * 0.55, 0.76)
        muted = _hsv_color(hue + offsets[1], relation_sat * 0.62, 0.49)

    return background, panel, accent, border, muted


def harmony_to_theme_changes(palette: tuple[str, str, str, str, str], appearance: str) -> dict[str, str]:
    if len(palette) != 5:
        raise ThemeBundleError("Harmony palette must contain exactly five colors")
    if appearance not in APPEARANCE_MODES:
        raise ThemeBundleError(f"Unsupported appearance mode: {appearance!r}")
    background, panel, accent, border, muted = [normalize_hex_color(value) for value in palette]
    text = "#f1f5f2" if appearance == "Dark" else "#202522"
    return {
        "background": background,
        "panel": panel,
        "sidebar": background,
        "border": border,
        "text": text,
        "muted": muted,
        "accent": accent,
        "input_bg": panel,
        "send_bg": border,
    }


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ThemeBundleError(f"{label} must be an object")
    return value


def validate_theme_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    bundle = dict(_require_mapping(bundle, "Theme bundle"))
    if bundle.get("version") != THEME_BUNDLE_VERSION:
        raise ThemeBundleError(
            f"Unsupported theme version {bundle.get('version')!r}; expected {THEME_BUNDLE_VERSION}"
        )
    name = str(bundle.get("name", "")).strip()
    if not name:
        raise ThemeBundleError("Theme name is required")

    palette_raw = _require_mapping(bundle.get("palette"), "palette")
    required_palette = (
        "background", "panel", "sidebar", "border", "text", "muted",
        "accent", "input_bg", "send_bg",
    )
    palette = {key: normalize_hex_color(str(palette_raw.get(key, ""))) for key in required_palette}

    typography_raw = _require_mapping(bundle.get("typography", {}), "typography")
    font = str(typography_raw.get("font", "Monospace"))
    text_size = str(typography_raw.get("text_size", "Default"))
    density = str(typography_raw.get("density", "Comfortable"))
    frosted = bool(typography_raw.get("frosted", False))
    if font not in FONT_KINDS:
        raise ThemeBundleError(f"Unsupported font: {font!r}")
    if text_size not in TEXT_SIZES:
        raise ThemeBundleError(f"Unsupported text size: {text_size!r}")
    if density not in DENSITIES:
        raise ThemeBundleError(f"Unsupported density: {density!r}")

    effect_raw = _require_mapping(bundle.get("effect", {}), "effect")
    effect_name = str(effect_raw.get("name", "Solid"))
    if effect_name not in KNOWN_EFFECTS:
        raise ThemeBundleError(f"Unsupported effect: {effect_name!r}")
    effect_color = normalize_hex_color(str(effect_raw.get("color", palette["accent"])))

    def number(key: str, default: float, minimum: float, maximum: float) -> float:
        try:
            value = float(effect_raw.get(key, default))
        except (TypeError, ValueError) as exc:
            raise ThemeBundleError(f"Effect {key} must be numeric") from exc
        if not minimum <= value <= maximum:
            raise ThemeBundleError(f"Effect {key} must be between {minimum} and {maximum}")
        return value

    normalized = {
        "version": THEME_BUNDLE_VERSION,
        "name": name,
        "palette": palette,
        "typography": {
            "font": font,
            "text_size": text_size,
            "density": density,
            "frosted": frosted,
        },
        "effect": {
            "name": effect_name,
            "color": effect_color,
            "speed": number("speed", 1.0, 0.05, 4.0),
            "intensity": number("intensity", 1.0, 0.05, 4.0),
            "quality": number("quality", 1.0, 0.25, 2.0),
            "size": number("size", 1.0, 0.25, 3.0),
            "paused": bool(effect_raw.get("paused", False)),
        },
    }
    return normalized


def make_theme_bundle(
    name: str,
    palette: Mapping[str, str],
    *,
    font: str,
    text_size: str,
    density: str,
    frosted: bool,
    effect: Mapping[str, Any],
) -> dict[str, Any]:
    return validate_theme_bundle(
        {
            "version": THEME_BUNDLE_VERSION,
            "name": name,
            "palette": dict(palette),
            "typography": {
                "font": font,
                "text_size": text_size,
                "density": density,
                "frosted": bool(frosted),
            },
            "effect": dict(effect),
        }
    )


def dumps_theme_bundle(bundle: Mapping[str, Any]) -> str:
    normalized = validate_theme_bundle(bundle)
    return json.dumps(normalized, indent=2, sort_keys=True) + "\n"


def loads_theme_bundle(text: str) -> dict[str, Any]:
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ThemeBundleError(f"Invalid theme JSON: {exc.msg}") from exc
    return validate_theme_bundle(_require_mapping(raw, "Theme bundle"))


def load_theme_bundle(path: str | Path) -> dict[str, Any]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ThemeBundleError(f"Could not read theme file: {exc}") from exc
    return loads_theme_bundle(text)


def save_theme_bundle_atomic(
    path: str | Path, bundle: Mapping[str, Any], *, protected_paths: tuple[str | Path, ...] = ()
) -> None:
    """Atomically write a valid theme unless ``path`` aliases active storage.

    The shell supplies its live SQLite, sidecar, and QSettings paths.  Target
    validation happens before directory creation so an unsafe rejected location
    cannot leave a new directory or temporary file behind.
    """

    try:
        target = validate_export_target(path, protected_paths)
    except ProtectedTargetError as exc:
        raise ThemeBundleError(str(exc)) from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = dumps_theme_bundle(bundle)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, dir=target.parent, prefix=f".{target.name}.", suffix=".tmp"
        ) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        os.replace(temp_path, target)
    except OSError as exc:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise ThemeBundleError(f"Could not write theme file: {exc}") from exc
