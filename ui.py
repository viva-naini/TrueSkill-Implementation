"""
Shared UI helpers (theme toggle, USR branding).
"""

from __future__ import annotations

from pathlib import Path
import streamlit as st


def _theme_css() -> str:
    # Light mode only - clean, readable styling
    bg = "#ffffff"
    panel = "#f6f8fa"
    text = "#0b1220"
    muted = "#4b5563"
    border = "#e5e7eb"
    input_bg = "#ffffff"
    # Tooltip colors - always dark background with light text for visibility
    tooltip_bg = "#f6f8fa"
    tooltip_text = "#ffffff"

    return f"""
<style>
  .stApp {{
    background: {bg};
    color: {text} !important;
  }}
  /* Ensure all text is readable */
  .stApp * {{
    color: {text} !important;
  }}
  /* Exception for input fields */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div > select,
  .stMultiselect > div > div > div {{
    background-color: {input_bg} !important;
    color: {text} !important;
  }}
  [data-testid="stSidebar"] > div {{
    background: {panel};
    border-right: 1px solid {border};
  }}
  .usr-brand h1, .usr-brand h2, .usr-brand h3, .usr-brand h4, .usr-brand h5, .usr-brand h6, .usr-brand p, .usr-brand div {{
    color: {text} !important;
  }}
  .usr-muted {{
    color: {muted} !important;
  }}
  /* Logo in sidebar */
  .usr-logo-container {{
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid {border};
  }}
  .usr-logo-container img {{
    height: auto;
    width: 100%;
    max-width: 200px;
  }}
  /* Tooltip styling */
  .usr-tooltip {{
    position: relative;
    display: inline-block;
    cursor: help;
  }}
  .usr-tooltip .usr-tooltiptext {{
    visibility: hidden;
    background-color: {tooltip_bg};
    color: {tooltip_text};
    text-align: left;
    padding: 10px 12px;
    border-radius: 6px;
    position: absolute;
    z-index: 10000;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    width: 280px;
    font-size: 0.85em;
    line-height: 1.5;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    white-space: normal;
    word-wrap: break-word;
    pointer-events: none;
  }}
  .usr-tooltip:hover .usr-tooltiptext {{
    visibility: visible;
    opacity: 1;
  }}
  /* Tooltip arrow */
  .usr-tooltip .usr-tooltiptext::after {{
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: {tooltip_bg} transparent transparent transparent;
  }}
  /* Make dataframe container feel closer to llm-stats vibe */
  [data-testid="stDataFrame"] {{
    border: 1px solid {border};
    border-radius: 10px;
    overflow: hidden;
  }}
  /* Ensure table text is readable */
  [data-testid="stDataFrame"] * {{
    color: {text} !important;
  }}
</style>
"""


def _encode_svg(logo_path: Path) -> str:
    """Read SVG file and encode as base64 for inline display."""
    import base64
    with open(logo_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def apply_theme_and_branding() -> None:
    # Apply light mode CSS
    st.markdown(_theme_css(), unsafe_allow_html=True)

    with st.sidebar:
        # Logo in sidebar above navigation
        logo_path = Path(__file__).parent / "assets" / "usr_logo.svg"
        if logo_path.exists():
            # Read SVG content and URL encode it for data URI
            import urllib.parse
            with open(logo_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            # URL encode the SVG content
            svg_encoded = urllib.parse.quote(svg_content)
            st.markdown(
                f'<div class="usr-logo-container">'
                f'<img src="data:image/svg+xml;charset=utf-8,{svg_encoded}" alt="USR Logo" />'
                f'</div>',
                unsafe_allow_html=True
            )
