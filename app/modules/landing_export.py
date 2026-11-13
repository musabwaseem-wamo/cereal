"""Build standalone HTML exports for campaign landing-page drafts."""

from __future__ import annotations

from html import escape
import re
from urllib.parse import urlparse


def _text(value: object, field: str, max_length: int = 1000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}' must be non-empty text.")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"'{field}' must be {max_length} characters or fewer.")
    return value


def validate_destination_url(value: object) -> str:
    if value is None or value == "":
        return "#get-started"
    if not isinstance(value, str) or len(value) > 2048:
        raise ValueError("The CTA destination must be a valid HTTPS or HTTP URL.")
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("The CTA destination must be a valid HTTPS or HTTP URL.")
    return value


def _escape(value: str) -> str:
    return escape(value, quote=True)


def build_standalone_landing_page(
    brand: object,
    headline: object,
    subhead: object,
    cta: object,
    bullets: object,
    destination_url: object = None,
    ad_copy: object = None,
    product: object = "your product",
    offer: object = "Review the offer details",
) -> str:
    """Return a self-contained HTML page with all styles embedded."""
    brand_text = _text(brand, "brand", 120)
    headline_text = _text(headline, "headline")
    subhead_text = _text(subhead, "subhead")
    cta_text = _text(cta, "CTA", 120)
    product_text = _text(product, "product", 300)
    offer_text = _text(offer, "offer", 300)
    if not isinstance(bullets, list) or not bullets or len(bullets) > 12:
        raise ValueError("The landing page must include between one and twelve benefit points.")
    bullet_items = [_text(item, "benefit", 500) for item in bullets]
    destination = validate_destination_url(destination_url)
    safe_destination = _escape(destination)
    safe_cta = _escape(cta_text)
    safe_brand = _escape(brand_text)
    if ad_copy is not None:
        if not isinstance(ad_copy, dict):
            raise ValueError("Selected ad copy must include a headline, body and CTA.")
        ad_headline = _escape(_text(ad_copy.get("headline"), "ad headline", 500))
        ad_body = _escape(_text(ad_copy.get("body"), "ad body", 2000))
        ad_cta = _escape(_text(ad_copy.get("cta"), "ad CTA", 120))
        ad_copy_section = f"""<section class="ad-copy" aria-label="Selected campaign ad copy">
      <span class="quote-mark" aria-hidden="true">“</span>
      <div>
        <p class="eyebrow">THE MESSAGE FROM YOUR AD</p>
        <h2>{ad_headline}</h2>
        <p>{ad_body}</p>
        <a class="primary-cta" href="{safe_destination}">{ad_cta} <span aria-hidden="true">→</span></a>
      </div>
    </section>"""
    else:
        ad_copy_section = ""

    benefits = "\n".join(
        f'          <li><span aria-hidden="true">✓</span><p>{_escape(item)}</p></li>'
        for item in bullet_items
    )
    placeholder_note = (
        '<p class="link-note">Before publishing, replace this button destination with your live signup or checkout URL.</p>'
        if destination == "#get-started"
        else ""
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{_escape(subhead_text)}">
  <title>{_escape(headline_text)} | {safe_brand}</title>
  <style>
    :root {{ color-scheme: light; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172b43; background: #f3f6fa; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; }}
    .page {{ min-height: 100vh; display: flex; flex-direction: column; }}
    header {{ width: min(1120px, calc(100% - 40px)); margin: 0 auto; padding: 24px 0; display: flex; justify-content: space-between; align-items: center; gap: 20px; }}
    .brand {{ display: flex; align-items: center; gap: 9px; font-size: 14px; font-weight: 800; letter-spacing: .04em; }}
    .brand-icon {{ width: 31px; height: 31px; display: grid; place-items: center; border-radius: 9px; background: #edf3fd; color: #3567c8; }}
    .brand-icon svg {{ width: 25px; height: 25px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }}
    .header-cta, .primary-cta {{ color: #fff; background: #172b43; text-decoration: none; border-radius: 6px; padding: 11px 16px; font-size: 12px; font-weight: 700; }}
    .header-cta span, .primary-cta span {{ color: #d8ed65; margin-left: 8px; }}
    main {{ flex: 1; }}
    .offer {{ display: flex; min-height: 39px; align-items: center; justify-content: center; gap: 12px; padding: 8px 18px; background: #d8ed65; text-align: center; }}
    .offer span {{ color: #566519; font-size: 9px; font-weight: 800; letter-spacing: .13em; }}
    .offer strong {{ color: #172b43; font-size: 12px; }}
    .hero {{ display: grid; grid-template-columns: 1.05fr .95fr; align-items: center; gap: 30px; min-height: 495px; overflow: hidden; padding: clamp(44px, 8vw, 86px) max(6vw, calc((100vw - 1080px) / 2)); background: linear-gradient(115deg,#f3f6fa 0%,#f3f6fa 53%,#e8eff8 100%); }}
    .hero-content {{ max-width: 580px; }}
    .eyebrow {{ color: #536d90; font-size: 10px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }}
    h1 {{ margin: 18px 0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: clamp(36px, 5vw, 58px); font-weight: 600; line-height: 1.04; letter-spacing: -.035em; }}
    .subhead {{ max-width: 510px; margin: 0 0 26px; color: #566a82; font-size: clamp(15px, 1.6vw, 17px); line-height: 1.7; }}
    .note {{ color: #7b8b9e; font-size: 11px; }}
    .product-stage {{ position: relative; display: grid; min-height: 305px; place-items: center; }}
    .product-stage::before {{ position: absolute; width: 255px; aspect-ratio: 1; border: 1px solid rgba(53,103,200,.18); border-radius: 50%; background: radial-gradient(circle,#d8ed6575 0 24%,#d8ed6520 25% 50%,transparent 51%); content: ""; }}
    .product-box {{ position: relative; display: flex; width: 205px; height: 260px; flex-direction: column; padding: 22px 19px; border: 1px solid rgba(255,255,255,.6); border-radius: 5px 5px 12px 12px; background: linear-gradient(150deg,#3567c8,#244e9b); box-shadow: 0 24px 38px rgba(23,43,67,.22); color: #fff; transform: rotate(4deg); }}
    .product-box span {{ display: -webkit-box; overflow: hidden; color: #cfdbeb; font: 600 9px/1.5 ui-monospace,monospace; letter-spacing: .07em; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }}
    .product-box strong {{ display: -webkit-box; margin-top: 30px; overflow: hidden; font-size: 19px; line-height: 1.15; text-overflow: ellipsis; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }}
    .product-box i {{ height: 25px; margin: auto -19px 14px; background: repeating-linear-gradient(135deg,#d8ed65 0 9px,#f7c45c 9px 18px); }}
    .product-box small {{ color: #d5e0ed; font-size: 7px; letter-spacing: .1em; }}
    .offer-note {{ position: absolute; right: 3%; bottom: 30px; max-width: 160px; padding: 14px; border: 1px solid #dce5ef; background: #fff; box-shadow: 0 12px 25px rgba(23,43,67,.1); transform: rotate(-4deg); }}
    .offer-note span {{ display: block; margin-bottom: 5px; color: #71859c; font-size: 8px; font-weight: 700; letter-spacing: .12em; }}
    .offer-note strong {{ color: #172b43; font-size: 11px; line-height: 1.4; }}
    .benefits {{ width: min(1050px, calc(100% - 40px)); margin: 0 auto; padding: 50px 0 60px; }}
    .ad-copy {{ display: grid; width: min(1050px, calc(100% - 40px)); grid-template-columns: 45px 1fr; gap: 18px; margin: 0 auto; padding: 35px 20px; border-top: 1px solid #e4eaf1; border-bottom: 1px solid #e4eaf1; background: #fff; }}
    .quote-mark {{ color: #3567c8; font: 800 56px/.8 Georgia,serif; }}
    .ad-copy h2, .benefits h2 {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: 600; letter-spacing: -.025em; }}
    .ad-copy h2 {{ margin: 10px 0; font-size: clamp(22px, 3vw, 31px); }}
    .ad-copy>div>p:not(.eyebrow) {{ max-width: 760px; color: #465a70; font-size: 15px; line-height: 1.65; }}
    .ad-copy .eyebrow {{ color: #3567c8; font-size: 10px; font-weight: 700; letter-spacing: .14em; }}
    .benefits h2 {{ margin: 8px 0 20px; font-size: 25px; }}
    .benefits ul {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 0; padding: 0; border-top: 1px solid #dce5ef; border-bottom: 1px solid #dce5ef; list-style: none; }}
    .benefits li {{ display: flex; gap: 12px; align-items: flex-start; padding: 20px; border-right: 1px solid #dce5ef; background: #fff; }}
    .benefits li:last-child {{ border-right: 0; }}
    .benefits li span {{ display: grid; width: 25px; height: 25px; flex: none; place-items: center; border-radius: 50%; background: #edf3fd; color: #3567c8; font-size: 11px; }}
    .benefits li p {{ margin: 0; color: #465a70; font-size: 13px; line-height: 1.6; }}
    .bottom-cta {{ display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 24px max(6vw, calc((100vw - 1080px) / 2)); background: #f3f6fa; }}
    .bottom-cta strong {{ display: block; margin-top: 7px; font-size: 17px; }}
    footer {{ padding: 22px 20px; border-top: 1px solid #dce5ef; color: #64758a; text-align: center; font-size: 11px; }}
    .link-note {{ margin: 14px auto 0; color: #566a82; font-size: 11px; }}
    @media (max-width: 700px) {{ header {{ width: calc(100% - 32px); padding: 17px 0; }} .hero {{ grid-template-columns: 1fr; gap: 0; padding: 54px 24px 15px; }} .hero-content {{ margin: auto; }} .product-stage {{ min-height: 250px; }} .product-box {{ width: 170px; height: 215px; }} .offer-note {{ right: 12%; }} .benefits {{ width: calc(100% - 32px); }} .bottom-cta {{ align-items: flex-start; flex-direction: column; padding: 24px; }} }}
    @media (max-width: 520px) {{ .offer {{ align-items: flex-start; flex-direction: column; gap: 4px; }} .brand {{ font-size: 11px; }} .header-cta {{ padding: 9px 11px; font-size: 10px; }} .hero {{ padding: 42px 20px 8px; }} .product-stage {{ min-height: 220px; }} .product-box {{ width: 145px; height: 185px; }} .product-box strong {{ margin-top: 20px; font-size: 15px; }} .offer-note {{ right: 3%; bottom: 20px; }} .benefits {{ width: calc(100% - 28px); }} .benefits ul {{ grid-template-columns: 1fr; }} .benefits li {{ border-right: 0; border-bottom: 1px solid #dce5ef; }} .benefits li:last-child {{ border-bottom: 0; }} }}
  </style>
</head>
<body>
  <div class="page">
    <header>
      <div class="brand"><span class="brand-icon" aria-hidden="true"><svg viewBox="0 0 40 40"><path d="M7 12.5 20 6l13 6.5v15L20 34l-13-6.5z"></path><path d="m7 12.5 13 6.7 13-6.7M20 19.2V34"></path></svg></span>{safe_brand}</div>
      <a class="header-cta" href="{safe_destination}">{safe_cta}<span aria-hidden="true">↗</span></a>
    </header>
    <main>
      <div class="offer"><span>THE OFFER</span><strong>{_escape(offer_text)}</strong></div>
      <section class="hero" id="get-started">
        <div class="hero-content">
          <div class="eyebrow">A CLOSER LOOK AT { _escape(product_text).upper() }</div>
          <h1>{_escape(headline_text)}</h1>
          <p class="subhead">{_escape(subhead_text)}</p>
          <a class="primary-cta" href="{safe_destination}">{safe_cta} <span aria-hidden="true">→</span></a>
          {placeholder_note}
          <p class="note">Explore the offer and see if it fits your needs.</p>
        </div>
        <div class="product-stage" aria-label="Decorative campaign artwork">
          <div class="product-box"><span>{_escape(product_text)}</span><strong>{safe_brand}</strong><i></i><small>MADE FOR YOUR ROUTINE</small></div>
          <div class="offer-note"><span>THE OFFER</span><strong>{_escape(offer_text)}</strong></div>
        </div>
      </section>
      {ad_copy_section}
      <section class="benefits" aria-labelledby="benefits-title">
        <p class="eyebrow">THE DETAILS THAT MATTER</p>
        <h2 id="benefits-title">A clearer look at what’s included.</h2>
        <ul>
{benefits}
        </ul>
      </section>
      <section class="bottom-cta"><div><p class="eyebrow">READY WHEN YOU ARE</p><strong>Take the next step on your terms.</strong></div><a class="header-cta" href="{safe_destination}">{safe_cta}<span aria-hidden="true">↗</span></a></section>
    </main>
    <footer>© {safe_brand}. Review all claims and offer details before publishing.</footer>
  </div>
</body>
</html>
"""


def landing_page_filename(brand: str) -> str:
    """Return a filesystem-safe name for the exported page."""
    slug = re.sub(r"[^a-z0-9]+", "-", brand.lower()).strip("-") or "campaign"
    return f"{slug[:60]}-landing-page.html"
