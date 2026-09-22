# Manual setup checklist — Orlant Shopify store

Things that must be done in the Shopify admin, by a human, because they are
outside the theme code or need credentials/approval the build cannot supply.

Kept up to date as the build progresses. Status legend:
`[x]` done · `[ ]` outstanding · `[~]` partly done

Store: `orlant-gujfiai0.myshopify.com`
Theme repo: <https://github.com/ryanliong/orlant-shopify-theme>

---

## 1. Already done

- [x] **Store timezone** → Settings › General › (GMT+08:00) Singapore.
      Was `America/New_York`; affects order timestamps, scheduled publishing,
      discount windows and every analytics report.
- [x] **Custom app + Admin API token** for build tooling.
      Scopes: `read/write_products`, `read/write_metaobject_definitions`,
      `read/write_metaobjects`, `read/write_files`, `read/write_content`.
- [x] **GitHub integration** → theme `orlant-shopify-theme/main` connected.
- [x] **Supporting pages created** — About, Contact, FAQ and System
      compatibility, each bound to its theme template. Copy is placeholder.

## 2. Needed before the theme can be finished

- [ ] **Currency formatting** → Settings › General › Currency formatting.
      Currently `${{amount}}`, so a S$1,299 rack renders as **$1,299.00** —
      ambiguous with USD on a four-figure purchase. Change both fields to
      `S${{amount}}` and `S${{amount}} SGD`.
- [ ] **Search & Discovery filters** — Shopify's free app, install then
      Settings › Filters. Price and Availability work out of the box; the
      brief also wants:
      - **Series** → add a filter on the product **tag** (values already set:
        `X Series`, `M Series`, `D Series`, `E Series`)
      - **Features** → add filters on the metafields `orlant.compare_heating`,
        `orlant.compare_sterilisation`, `orlant.compare_lighting`,
        `orlant.compare_app_control`
      The theme renders whatever filters this app exposes; it cannot create
      them.
- [ ] **Navigation menus** → Content › Menus. The header expects:
      Shop · Models · Compatibility · FAQ · Contact.
      Leave a placeholder item for the future store locator (brief §9.1).
- [ ] **Accessories collection** for the cart upsell ("You may also need").
      It currently points at `all-models`, so the cart offers other drying
      racks — fine as a placeholder, wrong for launch. Create a collection of
      spare poles, remotes and mounting plates, then repoint the
      **Orlant: cart upsell** section at it in the theme editor.
- [x] **Deleted the "Home page" (`frontpage`) collection** — a Shopify
      default that showed as a meaningless tile on `/collections`. The home
      page's featured section points at `all-models` instead.

## 3. Payments (start early — approval takes time)

- [ ] **Shopify Payments** → Settings › Payments. Covers Visa, Mastercard,
      Amex, Apple Pay, Google Pay.
- [ ] **HitPay** (Shopify App Store) → for **PayNow**, which Shopify Payments
      does **not** support in Singapore. Also carries Atome and ShopBack for
      later (brief §9.6).
      Needs a business account linked to the client's **UEN** — begin on day 1,
      approval is not instant.
- [ ] **Upload PayNow icon** → Theme settings › Orlant › Payment icons.
      Shopify draws icons only for methods it processes itself; PayNow, Atome
      and ShopBack must be uploaded as images (SVG or transparent PNG, ~80×50).
- [ ] **Test a real low-value transaction** on each method before launch.

## 4. Checkout branding

Settings › Checkout › Customize. Not theme-editable — Shopify owns checkout.

- [ ] Logo: Orlant logo, left-aligned
- [ ] Accent / primary button colour: `#4B2A73` (plum-700)
- [ ] Button label colour: `#FFFFFF`
- [ ] Error colour: leave Shopify default
- [ ] Heading font: Playfair Display · Body font: Work Sans
- [ ] Background: `#FFFFFF`

## 5. Content the client must supply

- [ ] **Product photography** — every product currently shares one placeholder
      crop set, so M2, D3 and E5 all show X1 imagery. Fine for layout review,
      wrong for a demo. Replace per product in Products › Media.
- [ ] **Brand logo** (SVG or 2x PNG) → Theme settings › Logo
- [ ] **Hero media** — the hero currently falls back to a Dawn placeholder.
      It takes a desktop image, a separate mobile image, and optionally an MP4
      background video (Content › Files, then paste the link into the section).
- [ ] **Home page video** — the "See it in a real flat" section points at a
      placeholder YouTube URL. Replace with the client's walkthrough.
- [ ] **Testimonials** — three placeholder quotes are in the theme editor.
      Replace with real customer words, with permission to publish them.
- [ ] **Real copy** for About, Contact, FAQ, System Compatibility pages
- [ ] **Policy pages** → Settings › Policies (refund, privacy, shipping, terms).
      Shopify generates templates; the client must review them.
- [ ] **Contact details** — address, opening hours, support email, phone
- [ ] **Social links** → Theme settings › Social media
- [ ] **WhatsApp number** → Theme settings › Orlant.
      Currently the placeholder `6591234567`; the button links to a dead
      number until this is changed.

## 6. Launch

- [ ] **Publish the theme** → Online Store › Themes › `orlant-shopify-theme/main`
      › Publish. Replaces the stock **Horizon** theme that ships with new
      stores.
- [ ] **Remove the storefront password** → Online Store › Preferences.
- [ ] **Connect the domain** (`orlant.com.sg`) → Settings › Domains.
      Plan the cutover from the existing non-Shopify site.
- [ ] **Delete the sample products** (`orlant-x1/m2/d3/e5-...`) if they were
      not overwritten with real ones, and the placeholder media with them.
- [ ] **Shipping rates** → Settings › Shipping. Installation is included in
      the price per the sample copy — confirm that is actually true.

## 7. Handover / security

- [ ] **Uninstall the build custom app** → kills the Admin API token.
      Do this before the store transfers to the client.
- [ ] **Delete `~/.orlant-admin-token`** from the build machine.
- [ ] Decide whether the client edits the theme directly on `main` (the GitHub
      integration writes editor changes straight back to the branch) or whether
      they should work on a separate branch.

---

## Notes

**Why some of this cannot be scripted.** The Admin API can create products,
collections and metafields, and does — see `scripts/`. It cannot install apps,
approve a payment gateway, set checkout branding, publish a theme or buy a
domain. Those are deliberately human-gated by Shopify.
