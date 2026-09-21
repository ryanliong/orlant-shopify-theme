/*
 * <orlant-sticky-atc> — reveals a fixed add-to-cart bar once the real buy
 * buttons leave the viewport.
 *
 * IntersectionObserver rather than a scroll listener: no per-frame work, and it
 * stays correct when the buy box shifts (accordion opening, image load).
 *
 * The bar holds no variant state of its own. Its button submits the real
 * product form through a `form` attribute, and the markup lives inside
 * <product-info>, which Dawn re-renders on every variant change — so price and
 * availability follow along without this element subscribing to anything.
 */
class OrlantStickyAtc extends HTMLElement {
  connectedCallback() {
    // Scope to this product section; a page could hold more than one.
    const root = this.closest('product-info') || document;
    this.target = root.querySelector('.product-form__buttons');

    if (!this.target || !('IntersectionObserver' in window)) {
      // Without a reference point the bar cannot know when to appear, so stay
      // hidden rather than covering the page permanently.
      this.hidden = true;
      return;
    }

    this.observer = new IntersectionObserver(
      ([entry]) => {
        this.hidden = entry.isIntersecting;
      },
      { rootMargin: '0px 0px -80px 0px' }
    );
    this.observer.observe(this.target);
  }

  disconnectedCallback() {
    this.observer?.disconnect();
  }
}

if (!customElements.get('orlant-sticky-atc')) {
  customElements.define('orlant-sticky-atc', OrlantStickyAtc);
}
