# Orlant — Shopify theme

Custom Online Store 2.0 theme for **Orlant International Pte Ltd** (Singapore),
selling ceiling-mounted smart drying racks. Built on **Shopify Dawn 16.0.0**.

- **Store:** `orlant-gujfiai0.myshopify.com`
- **Theme:** connected to this repo's `main` branch via Shopify's GitHub integration

> **The GitHub connection is two-way.** Edits made in the Shopify theme editor
> commit straight back to `main`. Pull before you push, or you will hit
> conflicts.

---

## Contents

1. [Getting set up](#getting-set-up)
2. [Sections](#sections)
3. [Metafields](#metafields)
4. [Theme settings](#theme-settings)
5. [Adding a product](#adding-a-product)
6. [Scripts](#scripts)
7. [Checkout and payments](#checkout-and-payments)
8. [Quality bar](#quality-bar)
9. [Conventions](#conventions)

---

## Getting set up

```bash
npm i -g @shopify/cli
git clone https://github.com/ryanliong/orlant-shopify-theme.git
cd orlant-shopify-theme
shopify theme dev --store orlant-gujfiai0.myshopify.com   # live preview
shopify theme check                                        # lint
python3 .orlant-validate.py                                # see Conventions
```

The store is password-protected until launch (Online Store › Preferences).

---

## Sections

Custom sections are prefixed `orlant-` so they sort together in the editor and
are obvious against Dawn's own files.

| Section | Used on | Notes |
|---|---|---|
| `orlant-hero` | Home | Image or muted looping video. Video is desktop-only; a separate mobile image is used instead. Falls back to a plum gradient when no media is set. |
| `orlant-trust-bar` | Home, About, Contact | 3–4 icon + text items |
| `orlant-feature-split` | Home, Compatibility, About | Media one side, text and bullets the other. Side flips per instance; stack two with the toggle reversed for alternating rows. |
| `orlant-compare` | Home, Product, Compatibility | Table driven by the `orlant.compare_*` metafields. On a product page the current model's column is highlighted automatically. |
| `orlant-testimonials` | Home | Quote, name, home type, star rating. Static until a reviews app is added. |
| `orlant-cta-banner` | Home, FAQ, Compatibility, About, Contact | Dark plum close with the champagne rule and a WhatsApp button |
| `orlant-product-tabs` | Product | Six metafield-fed panels. Tabs on desktop, accordions on mobile. |
| `orlant-cart-upsell` | Cart | "You may also need", from a chosen collection |

Reused from Dawn unchanged: `featured-collection`, `video`,
`collapsible-content`, `contact-form`, `main-*`.

**Product buy-box blocks** (reorderable in the editor): `orlant_series`,
`orlant_highlights`, `orlant_reassurance`, `orlant_whatsapp`.

---

## Metafields

All in the **`orlant`** namespace, on **Products**. Created by
`scripts/setup-metafields.py`.

| Key | Type | Used for |
|---|---|---|
| `series` | single line text | Label above the product title, e.g. "X Series" |
| `card_tagline` | single line text | One-line spec on listing cards |
| `badge` | single line text | Card badge, e.g. "New". Suppressed while the product is on sale, so it never stacks with Dawn's Sale badge. |
| `highlights` | list of single line text | Bullets under the buy box |
| `overview` | rich text | Overview tab |
| `specs` | list of `orlant_spec_row` | Specification table |
| `in_the_box` | rich text | What's in the box tab |
| `installation` | rich text | Installation & compatibility tab |
| `warranty` | rich text | Warranty tab |
| `faq` | list of `orlant_faq_item` | Product FAQ tab |
| `compare_max_load` | single line text | Comparison row, e.g. "35 kg" |
| `compare_drying_poles` | integer | Comparison row |
| `compare_heating` | boolean | Comparison row |
| `compare_sterilisation` | boolean | Comparison row |
| `compare_lighting` | boolean | Comparison row |
| `compare_app_control` | boolean | Comparison row |

**Metaobjects:** `orlant_spec_row` (label, value) and `orlant_faq_item`
(question, answer). Specs and FAQs are metaobjects rather than JSON so the
client edits labelled fields in admin instead of hand-writing JSON, where one
missing brace breaks the table. Spec rows are reusable across products.

**Every tab hides itself when its metafield is empty**, so a half-filled
product shows fewer tabs rather than empty ones.

> **Storefront access matters.** Definitions created through the Admin API
> default to `storefront: NONE`, which makes them invisible to Liquid — tabs
> render blank with no error to explain why. `setup-metafields.py` sets
> `PUBLIC_READ` and repairs any definition that is still `NONE`.

---

## Theme settings

**Theme settings › Orlant:**

- **WhatsApp number** — international format, digits only (`6591234567`). Blank
  hides every WhatsApp button. The product name and URL are appended to the
  message automatically.
- **Delivery message** — shown in the cart drawer, cart page and buy box
- **Reassurance row** — four icon + text items under every product
- **Payment icons** — Shopify draws icons for methods it processes. PayNow,
  Atome and ShopBack must be uploaded here as images.

**Colour schemes** (Theme settings › Colors):

| Scheme | Background | Text | Buttons | Use |
|---|---|---|---|---|
| 1 Light | white | ink | plum-700 | Default |
| 2 Lavender | `#F3EEF9` | ink | plum-700 | Soft bands |
| 3 Dark plum | `#2A1740` | white | champagne | Footer, CTA |
| 4 Plum solid | `#4B2A73` | white | white | Announcement bar |
| 5 Ink | `#1C1822` | white | champagne | Highest contrast |

Palette: plum-900 `#2A1740` · plum-700 `#4B2A73` · plum-500 `#7A52A8` ·
lavender `#F3EEF9` · champagne `#C9A86A` · ink `#1C1822`.

All pairs meet WCAG AA. Champagne is an accent only — rules, badges, small
highlights — never a large fill or body text.

> Focus rings are plum-500 on light schemes and **champagne on dark schemes**:
> plum-500 only reaches 2.78:1 on plum-900, below the 3:1 minimum for non-text
> UI. If you add more dark schemes, add their ids to the dark-scheme rule in
> `assets/orlant-tokens.css`.

---

## Adding a product

1. **Products › Add product** — title, description, price, images (first image
   is the listing thumbnail; a second enables hover-swap on cards).
2. **Tag it with its series** (`X Series`, `M Series`, …) plus
   `Smart Drying Rack`. Collections are automated on these tags, so a correctly
   tagged product files itself.
3. **Fill the `orlant` metafields** at the bottom of the product page. At
   minimum: `series`, `card_tagline`, `highlights`, `overview`.
4. **Specs and FAQs** — create `orlant_spec_row` / `orlant_faq_item` entries in
   Content › Metaobjects, then reference them from the product.
5. **Comparison table** — fill `compare_*` to have the product appear usefully
   in the comparison, then add it as a block in the **Orlant: model comparison**
   section.
6. **Check it is published** to the Online Store sales channel, or it 404s.

---

## Scripts

Python 3, no dependencies. All read the Admin API token from
`~/.orlant-admin-token` (never commit it — `.gitignore` guards it) and all are
idempotent.

```bash
SHOP=orlant-gujfiai0.myshopify.com python3 scripts/setup-metafields.py
SHOP=orlant-gujfiai0.myshopify.com python3 scripts/setup-collections.py
SHOP=orlant-gujfiai0.myshopify.com python3 scripts/setup-pages.py
SHOP=… MEDIA_DIR=/tmp/orlant-media python3 scripts/upload-placeholder-media.py
SHOP=… FILE=path/to/logo.svg      python3 scripts/upload-brand-files.py
SHOP=… python3 scripts/setup-sample-data.py   # test products — do not run on production
```

Required scopes: `read/write_products`, `read/write_metaobjects`,
`read/write_metaobject_definitions`, `read/write_files`, `read/write_content`.

---

## Checkout and payments

The theme's job ends at the cart. Checkout is Shopify's and is configured in
admin — see [MANUAL-SETUP.md](MANUAL-SETUP.md) for the full list, including:

- **Shopify Payments** for cards, Apple Pay and Google Pay
- **HitPay** for **PayNow** — Shopify Payments does not support PayNow in
  Singapore, and PayNow is what most Singapore buyers expect for a four-figure
  purchase. HitPay needs the client's UEN and approval is not instant, so start
  it early.
- **Checkout branding** — Settings › Checkout, with the exact values to enter

---

## Quality bar

`shopify theme check`: **0 errors**. Nine warnings remain, all in untouched
Dawn files.

Lighthouse, mobile, median of three runs (targets 80 / 90 / 90 / 90):

| Page | Performance | Accessibility | Best Practices | SEO |
|---|---|---|---|---|
| Home | 90 ✅ | 94 ✅ | 77 ❌ | 92 ✅ |
| Product | 82 ✅ | 93 ✅ | 77 ❌ | 100 ✅ |

**Best Practices cannot reach 90 from the theme.** The remaining failures are
Shopify's own Shop Pay integration setting third-party cookies, plus the
preview bar's untitled iframe. Neither is theme code.

Two further caveats on these numbers:

- They were measured against an **unpublished theme in preview**, where
  Shopify's preview bar adds ~367 KB (18% of page weight). Expect better once
  published. For scale: **this theme's own assets are 67 KB of a 1,995 KB page
  — about 3%.** The rest is Shopify platform code.
- Performance is noisy on a shared preview; individual product runs ranged
  59–89. Re-measure after launch on the published theme.

---

## Conventions

- **Prefix** custom sections, snippets and assets with `orlant-`.
- **No new dependencies.** Vanilla JS and Dawn's existing web-component
  patterns. No jQuery, no frameworks.
- **Nothing client-facing is hard-coded.** Text, images, colours and section
  order are all editable in the theme editor.
- **Extend Dawn, don't fork it.** `orlant-product-card.liquid` holds only the
  Orlant additions and is rendered from inside Dawn's `card-product.liquid`;
  duplicating that 600-line file would mean re-fixing every upstream bug twice.
- **Run `.orlant-validate.py` after editing any `templates/*.json` or
  `sections/*-group.json`.** Theme Check does not catch setting ids that no
  longer exist or range values off their step — Shopify silently drops both.
  This script catches them, and has already caught several.
