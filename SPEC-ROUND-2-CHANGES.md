# Spec — round 2 change requests

Five changes requested by the client on 6 Nov 2026. **Spec only; no work
started.** Each section covers what changes, how, what it depends on, and
how we will know it is done.

Status: `ready` = can start · `blocked` = waiting on an input

| # | Change | Status | Blocked on | Size |
|---|---|---|---|---|
| A | Black and gold colour scheme + sans-serif fonts | **ready** | Confirmed by client 7 Nov. Ryan's AI reference still useful | Large |
| B | Logo in the header | blocked | Vector logo (round 2 Q13) | Small |
| C | "Products" menu with series dropdown | **done** | Ryan, in admin | Small |
| D | Floating WhatsApp button | **done** | Built 7 Nov; number still the placeholder until round 2 Q15 | Small |
| E | Mailing list pop-up | ready | Simple sign-up, no discount. Privacy policy assumed to exist | Small–medium |
| F | Home page: function blocks with video slots | ready | Videos filmed later by Ryan; placeholders until then | Large |
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
- **Video slots take Shopify-hosted video**, not pasted links: Ryan uploads
  the file in Content → Files and picks it in the editor. The placeholder
  image doubles as the video's poster frame, so swapping a video in needs no
  other change.
- Colours come from colour schemes, so they follow A.

---

## A. Black and gold colour scheme, and sans-serif fonts

> **Confirmed by the client 7 Nov**, reversing the 6 Nov purple decision.
> Ryan's AI reference image is still the best way to settle the exact gold
> and how dark the pages go.

**Fonts (added 7 Nov):** move from the Playfair Display serif headings to a
sans-serif with a technical feel. Body text is already sans-serif (Work Sans)
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

1. **Agree the palette from the reference.** Starting proposal, to be adjusted
   to the reference:
   | Role | Proposal | Replaces |
   |---|---|---|
   | Base dark | near-black `#0E0D0B` (warm, not pure black) | plum-900 |
   | Raised dark (cards, bands) | `#1A1815` | plum-700 |
   | Gold, primary accent | `#C9A86A` (existing champagne) or a richer gold from the reference | plum as accent |
   | Gold, hover / highlight | lighter gold | plum-500 |
   | Light surface | warm off-white `#F7F4EE` | lavender |
   | Text on light | `#1C1822` (existing ink) | — |
2. **Decide the page rhythm.** All-dark pages get heavy and hard to read in
   long sections such as specs and FAQ. Proposal: dark header, hero, comparison
   table, CTA and footer; off-white bands for product details, FAQ and long
   text. To be confirmed against the reference.
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

> **Done 7 Nov.** Settings in Theme settings → Orlant. Uses the placeholder
> number until the client confirms theirs (round 2 Q15).

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
**One function per block, each with a video slot**, filled with placeholders
until Ryan films the videos. Image slots never left blank or white.

**Need from Ryan:** nereos.sg blocks automated page reads and its home page
has no video blocks, so I couldn't see the layout you mean. Send 2–3
screenshots of the blocks you like, or the exact page URL.

**Approach:** a new section, `orlant-function-block`. It's a reusable row:
video or image on one side, heading, short description and 2–3 key figures
on the other, alternating sides down the page. It replaces the single
"Why smart drying" split. Each block has:
- **Video:** Shopify-hosted, autoplay muted and looped, with no sound and no
  controls, like a moving photo. Plays only while on screen, and not at all
  under reduced-motion settings (the poster shows instead).
- **Poster / placeholder image:** pre-filled from the client's renders and
  installation photos, chosen per function, so the page looks finished
  before any filming.
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

**Done when:** every block shows a relevant image; dropping a video into a
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

**Approach:** more vertical padding (around double), more space between
items, larger icons (from 26 to around 40 px), and title and supporting line
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
