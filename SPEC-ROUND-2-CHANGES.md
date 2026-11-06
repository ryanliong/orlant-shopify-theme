# Spec — round 2 change requests

Five changes requested by the client on 6 Nov 2026. **Spec only; no work
started.** Each section covers what changes, how, what it depends on, and
how we will know it is done.

Status: `ready` = can start · `blocked` = waiting on an input

| # | Change | Status | Blocked on | Size |
|---|---|---|---|---|
| A | Black and gold colour scheme | blocked | Client confirms reversal of purple; Ryan's AI reference | Large |
| B | Logo in the header | blocked | Vector logo (round 2 Q13) | Small |
| C | "Products" menu with series dropdown | ready* | *Line-up (round 2 Q1, Q2) only affects which items appear | Small |
| D | Floating WhatsApp button | ready* | *Confirmed number (round 2 Q15); placeholder until then | Small |
| E | Mailing list pop-up | blocked | Incentive, consent wording, platform choice | Medium |

**Suggested order: A, then B–E.** The colour scheme decides how every other
piece looks: the logo needs a version for a dark header, and the button,
pop-up and dropdown all take their colours from it. Building them first means
restyling them twice.

---

## A. Black and gold colour scheme

**Request:** the current look is "a bit too monochrome". Lean into heavy
black and gold for a premium feel. The client has no fixed preference; Ryan
will produce an AI reference image to align on.

**This reverses a decision.** On 6 Nov the client confirmed "Orlant and the
purple colour scheme". Black and gold replaces that. Get it confirmed in
writing, together with whether purple survives at all, before starting.
This is the biggest change in the round, so it is the one not to redo.

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
   - On product pages the sticky add-to-cart bar takes the bottom of the
     screen; the button moves up above it while the bar is showing.
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

**Decisions needed first:**
1. **Incentive.** Pop-ups with an offer ("$30 off your first order",
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

**Recommendation: Shopify Forms**, styled to match. It handles consent and
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

## New questions for the client

They asked for questions in one batch, so these wait for the next round
rather than going out now.

1. **Colour scheme:** confirm moving from purple to black and gold, reversing
   the 6 Nov decision. Should purple remain anywhere?
2. **Logo:** please include a light (white or gold) version for the dark
   header and footer, as well as the dark version.
3. **Mailing list:** is there a sign-up offer? What will subscribers receive,
   and how often? Who will send the emails?
4. **Privacy policy:** a mailing list needs one. Does Orlant have one we can
   use, or should we start from Shopify's template for them to review?
