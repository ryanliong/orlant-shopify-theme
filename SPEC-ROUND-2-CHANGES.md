# Spec — round 2 change requests

Five changes requested by the client on 6 Nov 2026. **Spec only; no work
started.** Each section covers what changes, how, what it depends on, and
how we will know it is done.

Status: `ready` = can start · `blocked` = waiting on an input

| # | Change | Status | Blocked on | Size |
|---|---|---|---|---|
| A | Black and gold colour scheme + sans-serif fonts | **done** | Built; awaiting client approval of home and product page | Large |
| B | Logo in the header | blocked | Vector logo (round 2 Q13) | Small |
| C | "Products" menu with series dropdown | **done** | Ryan, in admin | Small |
| D | Floating WhatsApp button | **done** | Built and checked by Ryan on the live store; number still the placeholder until round 2 Q15 | Small |
| E | Mailing list pop-up | ready | Simple sign-up, no discount. Privacy policy assumed to exist | Small–medium |
| F | Home page: function blocks (image slot, video optional) | ready | Nereos screenshots received. Image or video decided per block later | Large |
| G | Capabilities showcase (GoodLiving style) | ready | — | Medium |
| H | Trust bar: more room | ready | — | Small |
| I | Product page: point-form features, video slots, bigger price | ready* | *Sale price display depends on round 2 Q3 | Medium |
| J | Comparison table thumbnails | ready | — | Small |

**Order (updated 7 Nov):** A first — colours and fonts change the look of
everything else, so building F–J against purple would mean judging them
twice. Then F, G and I (the bulk of the visible change), then H, J and E.

Rules for everything in F–J:
- **No empty or white boxes.** Every image or video slot without content
  shows a placeholder: a product render or installation photo from the
  client's assets, never a blank frame or a stock placeholder.
- **Every media slot is an image slot first.** Each slot can also take a
  video, added later if the block suits one; the image then becomes the
  video's poster frame, so adding a video needs no other change. Videos are
  Shopify-hosted, not pasted links: Ryan uploads the file in Content → Files
  and picks it in the editor.
- Colours come from colour schemes, so they follow A.

---

## A. Black and gold colour scheme, and sans-serif fonts

> **Built.** Waiting on the client's approval of the home page and one product
> page. What was done:
> - **Fonts: Saira** (bold headings, regular body), the closest match in
>   Shopify's font library to the catalogue's lettering (compared against
>   Titillium Web, Chakra Petch, Rajdhani and Barlow). The client can still
>   change it in Theme settings → Typography.
> - **Schemes:** 1 Black (default), 2 Brown panel, 3 Deep black (hero, CTA,
>   footer), 4 Gold (brushed-gold gradient: announcement bar, sale badge),
>   5 Ivory (FAQ page). README has the table.
> - **Accent colour follows the scheme** (`--orlant-accent`): gold on dark,
>   black on gold, dark gold on ivory. No purple left in the theme.
> - **Favicon** redrawn in black and gold (a ceiling rack mark), still a
>   placeholder until the logo arrives.
> - **Policy pages stay dark**: Shopify renders them with the default scheme,
>   and off-white text on black is 17:1, so they read fine. Only the FAQ page
>   uses ivory.
> - Fixed on the way: the comparison table made home and product pages 555px
>   wide on phones (now fits 390px).
> - Checks: theme check (same 9 Dawn warnings), Lighthouse accessibility 97
>   on home and product page.
>
> **Noticed, not fixed:** the product renders have white backgrounds, which
> stand out as white boxes on the black pages. The catalogue shows the same
> renders on black. Options: ask the client for transparent PNGs, or cut out
> the backgrounds ourselves.
>
> **Confirmed by the client 7 Nov**, reversing the 6 Nov purple decision.
> **Colour reference: the H2 catalogue** (Ryan's call, instead of an AI
> image). The palette below is taken from the catalogue's own artwork.

**Fonts (added 7 Nov):** move from the Playfair Display serif headings to a
sans-serif with a technical feel. The catalogue uses a bold, slightly
rounded sans for its headings; it can't be identified from the file, so the
shortlist aims for the same feel. Body text is already sans-serif (Work Sans)
and can stay, or switch to match. Candidates are picked from Shopify's font
library so the client can still change them in the editor; I'll shortlist
2–3 options as screenshots of the home page heading and a product page for
you to choose from. Heavier weights for headings, generous letter-spacing on
small uppercase labels, and numbers set in the same family so spec figures
line up.

**Request:** the current look is "a bit too monochrome". Lean into heavy
black and gold for a premium feel. The client has no fixed preference; Ryan
will produce an AI reference image to align on.

**Purple:** assumed to be dropped entirely. Confirm if any should survive.

**Context:** their H2 catalogue is already black and gold, and its gold is
close to the theme's existing champagne accent (`#C9A86A`). The direction
matches how they already present the brand in print.

**Approach:** the palette lives in the theme's colour schemes and design
tokens, not in individual pages, so this is a settings and token change, not a
rebuild.

1. **Palette, taken from the H2 catalogue.** The catalogue's text is
   outlined artwork, so its fonts can't be read from the file, but its fill
   colours can. What it uses:
   - **Black backgrounds:** `#010102` and `#151515`, with gold sparkle and
     light-streak imagery.
   - **Warm dark brown** `#231916` behind panels.
   - **Gold title bars** as a horizontal gradient: deep gold `#BB8C17` at
     the ends, through `#D3B05C`, to near-white `#FCF0D5` in the centre, like
     brushed metal. Black bold text on top.
   - **Thin gold outlines** around each product's spec panel, and pale gold
     `#F3E2BA` for small headings ("ORLANT Brand Promise").
   - **Red price tags** for retail and promotional prices.

   Theme palette from that:
   | Role | Value | From the catalogue | Replaces |
   |---|---|---|---|
   | Base dark | `#0B0B0C` | page black, lifted a touch so it isn't pure black on screens | plum-900 |
   | Raised dark (cards, bands) | `#1E1714` | the warm brown panels | plum-700 |
   | Gold, primary accent and buttons | `#D3B05C` | mid-point of the gold bars | plum as accent |
   | Gold, deep (borders, pressed) | `#BB8C17` | ends of the gold bars | — |
   | Gold, pale (small headings on dark) | `#F3E2BA` | the pale gold headings | plum-500 |
   | Gold gradient (feature bars, CTA band) | `#BB8C17 → #F3E2BA → #BB8C17` | the title bars | — |
   | Text on dark | `#F2EFEA`, muted `#B9B3A8` | — | — |
   | Light surface | warm off-white `#F7F4EE` | — | lavender |
   | Text on light | `#1C1822` (existing ink) | — | — |
   | Gold on light surfaces | `#8A6510` (darker gold) | — | — |

   **Contrast, checked:** gold on black 9.5:1, gold on the brown cards
   8.5:1, black text on gold buttons 9.5:1, muted text on black 9.4:1, dark
   gold on off-white 4.8:1. All pass AA. Catalogue gold on white is only
   3.1:1, which is why light sections use the darker gold.

   **Red sale price:** the catalogue marks prices in red tags. For the sale
   price on the product page (I) we keep it gold, not red, unless the client
   asks; red would be the only non-gold colour on the site. To confirm when
   the price display is shown to the client.
2. **Decide the page rhythm.** The catalogue is black on every page, so the
   site leans dark: header, hero, function blocks, capabilities, comparison
   table, CTA and footer all dark. All-dark pages get heavy in long text, so
   FAQ and policy pages use the off-white surface. Product pages stay dark,
   with the spec table in a brown panel with a thin gold outline, as in the
   catalogue.
3. **Remap the 5 colour schemes** in theme settings, and the `--orlant-*`
   tokens in `assets/orlant-tokens.css`.
4. **Fix the places that assume purple:** the hero gradient fallback
   (`assets/orlant-hero.css`), the feature-split placeholder, the focus ring
   rule for dark schemes, and the favicon (plum background).
5. **Buttons:** gold buttons with dark text on dark sections; dark buttons on
   light sections. Gold text is not used for body copy.
6. **Feature icon tiles** already take their colour from a scheme, so they
   follow automatically.

**Done when:**
- Every text/background pair meets WCAG AA (4.5:1 for text, 3:1 for UI and
  focus rings), checked with the same contrast script as round 1.
- Lighthouse accessibility stays at or above 90 on home and product pages.
- No purple left anywhere: grep for the old hex values comes back empty.
- Client approves the home page and one product page.

**Risk:** gold on near-black looks premium, but gold on white often fails
contrast. Gold is reserved for dark backgrounds and for accents too large to
need text contrast.

---

## B. Logo in the header

**Request:** replace the text "Orlant" in the header with the real logo once
the client sends the file.

**Depends on:** round 2 Q13, the vector logo. **If A goes ahead, the header is
dark**, so we need a light-on-dark version, not only the dark-on-light one we
asked for.

**Approach:**
1. Upload both versions with `scripts/upload-brand-files.py`.
2. Set the header logo (Theme settings → Logo) and logo width; check it on
   mobile (around 120px wide) and desktop.
3. Footer logo on the dark footer: use the light version.
4. **Overlay header over the hero:** when the header sits transparently over
   the hero, it needs the light version too. The header section gets a second
   logo setting used only while overlaying.
5. Replace the placeholder favicon with a mark from the logo.

**Done when:** the logo is sharp at 1x and 2x, readable on every header state
(solid, transparent over hero, sticky on scroll), and links to the home page
with "Orlant" as its accessible name.

---

## C. "Products" menu with a series dropdown

> **Done by Ryan, 7 Nov**, in Content → Menus.

**Request:** rename "Catalog" to "Products" and add a dropdown listing the
series, each leading to that series' collection page.

**Approach:** this is mostly navigation data, not theme code. The header is
already set to dropdown menus.

1. In **Content → Menus → Main menu**: rename "Catalog" to "Products" and
   point it at `/collections/all-models`.
2. Nest the series under it:
   - All models → `/collections/all-models`
   - M Series → `/collections/m-series`
   - D Series → `/collections/d-series`
   - X Series → `/collections/x-series` *(only if round 2 Q1 says the X6 is
     still sold)*
   - E Series → *(only if round 2 Q2 says the E13EL is sold; needs a new
     collection)*
3. Check the dropdown on desktop (hover and keyboard) and in the mobile menu
   drawer, which shows nested items as a sub-menu.

**Optional upgrade:** Dawn also offers a **mega menu**, a wide panel instead of
a list. It could show each series with a product image and a one-line
description, at no extra code. Worth showing the client as an option once
the colour scheme is settled.

**Can I do it, or do you?** Menus can be edited by script, but the build app
needs one more scope, `write_online_store_navigation`. Either add the scope or
make the change by hand in admin. It's 5 minutes either way, and the menu is
the kind of thing the client will want to edit themselves later.

**Done when:** "Products" opens a dropdown on desktop and a sub-menu on
mobile, every item goes to a populated collection, and discontinued series
are not listed.

---

## D. Floating WhatsApp button

> **Done 7 Nov; checked by Ryan on the live store.** Settings in Theme
> settings → Orlant. Uses the placeholder number until the client confirms
> theirs (round 2 Q15).

**Request:** a "message us" bubble at the bottom right that opens WhatsApp.

**Approach:** a new snippet, `snippets/orlant-whatsapp-float.liquid`, rendered
once in `layout/theme.liquid`. It reuses the existing WhatsApp number and
greeting from Theme settings → Orlant, so there is one number for the whole
site.

1. **Behaviour:** links to `wa.me/<number>?text=<greeting>`. On a product page
   the greeting includes the product name and link, as the product page
   button already does. Opens in a new tab or the WhatsApp app.
2. **Look:** a round button, around 56px, with the WhatsApp icon. Colours
   follow scheme A. An optional short label ("Chat with us") on desktop only.
3. **Settings** in Theme settings → Orlant: show or hide, label text, which
   side, and a "hide on these pages" option (cart by default).
4. **Collisions on mobile:**
   - On phones, product pages show a full-width add-to-cart bar along the
     bottom once the main Add to cart button scrolls out of view (desktop never
     shows it). The button moves up above the bar while it is showing.
     Everywhere else the bottom-right corner is free.
   - The mailing list pop-up (E) and the button must not overlap.
   - Clear of the iPhone home indicator (safe area).
5. **Hidden entirely** when no number is set, as the product page button
   already is.
6. **Accessibility:** a real link with an accessible name ("Chat with Orlant on
   WhatsApp"), visible focus ring, no attention-seeking animation, and none
   at all for `prefers-reduced-motion`.

**Depends on:** the confirmed number (round 2 Q15). The site currently has the
placeholder `6591234567`; build with that and swap it when confirmed.

**Done when:** it opens the right chat with a prefilled message on iPhone,
Android and desktop, never covers the add-to-cart bar or other buttons, and
doesn't lower Lighthouse performance (a small inline SVG, no scripts loaded
from WhatsApp).

---

## E. Mailing list pop-up

**Request:** a "join our mailing list" pop-up when people arrive.

**Decided 6 Nov:** a simple "join our mailing list for updates" sign-up. No
discount or other incentive.

**Decided 7 Nov:** what subscribers receive is not a concern for now. The
privacy policy is assumed to exist; the client is told one is needed.

**Originally open (now settled):**
1. ~~**Incentive.**~~ *Not needed — no discount.* Pop-ups with an offer ("$30 off your first order",
   "first to hear about roadshow deals") convert far better than a plain
   "join our list". Is there one? If it's a discount, the client must create
   the discount code.
2. **What subscribers get, and how often.** This sets the wording, and
   whether someone needs to send the emails (Shopify Email is free for a
   basic volume).
3. **Consent wording (PDPA).** Singapore's PDPA requires clear consent for
   marketing messages. Proposal: "By subscribing you agree to receive
   marketing emails from Orlant. Unsubscribe anytime." with a link to the
   privacy policy, which still needs writing.
4. **Platform**, below.

**Platform: theme pop-up vs Shopify Forms.**

| | Built into the theme | Shopify Forms app (free, by Shopify) |
|---|---|---|
| Look | Exactly on brand | Configurable, close to on brand |
| Consent record | Tags the customer as subscribed | Records consent properly, built for it |
| Timing and targeting rules | We build them | Built in |
| Discount on sign-up | Shown, but code created by hand | Built in |
| Reports | None | Sign-up stats |
| Client edits it | In the theme editor | In the app |

**Recommendation: still Shopify Forms**, styled to match — even without a
discount, it records PDPA consent properly and reports sign-ups. It handles consent and
discounts properly and gives the client reporting, for less code to maintain.
A custom pop-up only makes sense if Forms can't match the look closely
enough.

**Reference (Nereos):** a white card centred over a dimmed page: logo in a
small circle, bold heading, two lines of pitch, email field, full-width black
"Subscribe" button, and a consent line with the privacy policy link
underneath. Ours follows that layout in the black and gold scheme: dark card,
gold button, no prize or discount wording. On desktop it's a centred card as
Nereos does; on phones it stays a slide-up panel (below).

**Behaviour, either way:**
- **Not on arrival.** Show after about 10 seconds or halfway down a page, and
  on desktop optionally when the cursor leaves the page. An instant pop-up is
  the most-closed kind.
- **Once.** If closed, don't show again for 30 days; if subscribed, never.
- **Not on cart or checkout,** and not to people arriving from an email link.
- **Mobile:** a slide-up panel at the bottom, not a full-screen overlay. Google
  penalises pages where a pop-up covers the content on mobile, which would
  hurt search ranking.
- **Accessible:** focus moves into it, Escape closes it, and the close button
  is large and labelled.
- Doesn't collide with the WhatsApp button (D) or the sticky add-to-cart bar.

**Done when:** sign-ups appear in Shopify Customers marked as accepting
marketing, the pop-up follows the timing and once-only rules, it passes the
accessibility checks, and Lighthouse SEO and accessibility hold their scores.

---

## F. Home page: function blocks with video slots

**Request:** more blocks of information on the home page, following nereos.sg.
**One function per block.** Image slots never left blank or white.

**Updated after Ryan's input:** not every block needs a video. **Each block
gets an image placeholder**, and whether a block is better as an image or a
video is decided later, block by block. A video can be dropped into any
block without other changes.

**Nereos home page, from Ryan's screenshots**, top to bottom:
1. **Full-width video hero**: autoplaying video, big bold headline, a price
   line ("From $1399 installed") and one dark button.
2. **Trust row**: section heading, then 4 columns of a thin outline icon,
   bold title and one supporting line, with a divider underneath.
3. **Shop by category**: large image cards, one per product line.
4. **"Why choose" cards**: 4 light grey rounded cards, each with a black
   square icon tile, bold title and one line.
5. **Customer video carousel**: portrait video cards (YouTube Shorts and
   TikTok embeds) with arrow buttons.
6. **"Loved by Singaporeans"**: photo carousel of customers next to the
   product.
7. **Reviews**: star rating summary ("based on 1,920+ reviews", Judge.me)
   and review cards with photos.
8. **Black footer** with 4 columns, social icons and a WhatsApp bubble.

What carries over to Orlant:
- **The rhythm:** short sections, each with one centred heading and a row of
  equal cards or columns. Generous white space between sections. This is
  what "give it more room" (H) means in practice.
- **The video hero:** our hero section gets the same optional video slot,
  with the current banner as its poster.
- **Trust row and "why choose" cards:** these are the layouts for H and G.
- **Not carried over yet:** the customer video carousel, the customer photo
  carousel and the review widget all need real customer content (videos,
  photos, a reviews app) that Orlant doesn't have yet. The section types
  can be added when there's content; empty or invented testimonials would
  hurt more than help.

The function blocks themselves go beyond Nereos, whose home page has none:
they come from the client's request for one block per function.

**Approach:** a new section, `orlant-function-block`. It's a reusable row:
image (or video) on one side, heading, short description and 2–3 key
figures on the other, alternating sides down the page. It replaces the
single "Why smart drying" split. Each block has:
- **Image:** required, pre-filled from the client's renders and installation
  photos, chosen per function, so the page looks finished from day one.
- **Video (optional):** Shopify-hosted, autoplay muted and looped, with no
  sound and no controls, like a moving photo. When set, the image becomes
  its poster. Plays only while on screen, and not at all under
  reduced-motion settings (the image shows instead).
- **Heading, text, figures** (e.g. "6 EC blowers", "2200 RPM").

**Proposed blocks**, one per function, all from the H2 catalogue:
| # | Function | Placeholder image |
|---|---|---|
| 1 | Rapid drying — EC cross-flow blowers, hot and cold airflow | M6L render, airflow side |
| 2 | PTC heating | M6 render, underside |
| 3 | UV disinfection and ioniser | M5 render, light panel |
| 4 | 6-bar telescopic rails, full span | X6S/M6 render with rails extended |
| 5 | One-touch lifting and height control | Installation photo, rack lowered |
| 6 | Overweight alarm and bidirectional resistance protection | M6 render, frame detail |
| 7 | App and voice control | Installation photo + app icon |
| 8 | Ultra-thin 15 cm body | Installation photo flush to ceiling |
| 9 | 304 stainless steel cables, corrosion resistance | Render close-up |
| 10 | LED panel lighting | Installation photo, light on |

Ten is a lot for one page; the order puts the strongest selling points
first and the client can hide or reorder any of them in the editor.

**Done when:** every block shows a relevant image; adding a video to any
block needs no other change; the page stays fast (videos load only near the
screen, Lighthouse performance stays at or above 80).

---

## G. Capabilities showcase (GoodLiving style)

**Request:** show specs and capabilities the way goodliving.sg does.

GoodLiving uses an **icon grid**: 8 cards, each with an icon, a bold title
and one line of text, plus a separate "why trust us" row.

**Approach:** a new section, `orlant-capabilities`:
1. **Headline figures row:** 4 large numbers with labels, e.g. **55 kg** max
   load, **2200 RPM** blowers, **15 cm** ultra-thin, **5-year** motor
   warranty.
2. **Icon grid:** 8 cards, icon + title + one line. The client's feature icons
   are white on transparent, so on the black theme they finally sit on the
   background they were designed for.
3. Content is picked per block in the editor; the home page gets
   range-wide capabilities.

On the home page it sits after the hero and trust bar, before the function
blocks: the grid gives the summary, the blocks give the detail.

---

## H. Trust bar: give it more room

**Request:** the "Local stock … Since 2005" strip looks squashed.

**Reference:** Nereos' "Trusted Support From Purchase to Installation" row:
a centred section heading, then 4 columns of a thin outline icon, bold title
and one supporting line, with plenty of space around it and a thin divider
below.

**Approach:** add a section heading, more vertical padding (around double),
more space between items, larger icons (from 26 to around 40 px), and title and supporting line
on separate lines with more line height. Desktop stays 4 across; phones go
from 2×2 to a single column if the 2×2 still feels tight.

---

## I. Product page

**1. Features as point form, in a fixed order.** Replace the paragraph
description with a bullet list generated from the product's spec data, so
every product lists features **in the same order**: the ones every model
has first, model-specific ones last. Reading two product pages side by side,
the top of the list matches and only the bottom differs.

Proposed order (from the H2 catalogue):
| Order | Feature | On which models |
|---|---|---|
| 1 | Poles (length range × number) | all |
| 2 | PTC heaters × 4 | all |
| 3 | EC cross-flow blowers (4 or 6) | all |
| 4 | Overweight alarm (45 or 55 kg) | all |
| 5 | Bidirectional resistance protection | all |
| 6 | LED panel light (3-tone on M6) | all |
| 7 | Ioniser | all |
| 8 | UV disinfection | M5, M6 |
| 9 | Mobile app control | M5, M6 |
| 10 | Function display | M5, M6 |
| 11 | Multiple support | D6 |
| 12 | Voice control | M6 |
| 13 | Ultra-thin 15 cm design | M6 |

This needs three new spec fields the catalogue lists but the store doesn't
hold yet: bidirectional resistance protection, function display and
multiple support. **Question for the client:** what is "multiple support"
on the D6? (Added to the next batch.)

**2. Video slots.** Two kinds:
- **The model's own videos** go in the product's media, next to its photos.
  The gallery already plays video, so this needs no theme work; Ryan uploads
  them in the product's admin page.
- **Function videos** reuse the home page function blocks (F) below the
  product details, filtered to the functions that model has. One filmed
  video of the heater serves every model with a heater.

**3. Price.** Larger price text (from around 18 to around 28 px) and, when a
model is discounted, retail struck through beside the sale price and a
"Save $X" label. **Whether models are discounted is round 2 Q3** (retail vs
promotional); the display is built either way and shows only when a sale
price is set.

---

## J. Comparison table thumbnails

**Request:** small product images in "Compare the range", because names alone
make it hard to tell what is being compared.

**Approach:** each model's column header gets its main image (around 120 px,
square, linked to the product) above the name and price. On phones, where
the table scrolls sideways, the images shrink to around 72 px so the table
doesn't get taller than the screen.

---

## New questions for the client

They asked for questions in one batch, so these wait for the next round
rather than going out now.

5. **"Multiple support" on the D6** — what does it refer to? (Needed for the
   point-form feature list, I.)

1. ~~Colour scheme~~ — *on hold; not asking for now.*
2. **Logo:** please include a light (white) version for the dark footer, as
   well as the dark version.
3. ~~Mailing list contents~~ — *not asking for now (7 Nov).*
4. **Privacy policy (inform, not ask):** the mailing list sign-up links to
   Orlant's privacy policy, as Singapore's PDPA expects. We are assuming they
   have one; please send it so it can be added to the site.
