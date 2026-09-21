/*
 * <orlant-tabs> — accordion on mobile, tab strip on desktop.
 *
 * One set of buttons serves both layouts (CSS `order` hoists them into a strip
 * on desktop), so the ARIA has to be rebuilt when the breakpoint changes:
 * tab/tabpanel + aria-selected for the strip, button + aria-expanded for the
 * accordion. Announcing tabs while the user sees an accordion is worse than no
 * ARIA at all, which is why this is driven by the same media query as the CSS.
 */
class OrlantTabs extends HTMLElement {
  static DESKTOP = '(min-width: 750px)';

  connectedCallback() {
    this.triggers = Array.from(this.querySelectorAll('.orlant-tabs__trigger'));
    this.panels = Array.from(this.querySelectorAll('.orlant-tabs__panel'));
    if (!this.triggers.length) return;

    // Mobile opens the first panel so the section is never a wall of closed
    // bars; desktop always has exactly one panel showing.
    this.selected = 0;
    this.openOnMobile = new Set([0]);

    this.mq = window.matchMedia(OrlantTabs.DESKTOP);
    this.onBreakpoint = this.onBreakpoint.bind(this);
    this.mq.addEventListener('change', this.onBreakpoint);

    this.triggers.forEach((trigger) => {
      trigger.addEventListener('click', () => this.onClick(Number(trigger.dataset.index)));
      trigger.addEventListener('keydown', (event) => this.onKeydown(event));
    });

    this.render();
  }

  disconnectedCallback() {
    this.mq?.removeEventListener('change', this.onBreakpoint);
  }

  get isDesktop() {
    return this.mq.matches;
  }

  onBreakpoint() {
    // Carry the open panel across the breakpoint so the reader does not lose
    // their place on rotate or resize.
    if (this.isDesktop) {
      const firstOpen = Math.min(...(this.openOnMobile.size ? this.openOnMobile : [0]));
      this.selected = firstOpen;
    } else {
      this.openOnMobile = new Set([this.selected]);
    }
    this.render();
  }

  onClick(index) {
    if (this.isDesktop) {
      this.selected = index;
    } else if (this.openOnMobile.has(index)) {
      this.openOnMobile.delete(index);
    } else {
      this.openOnMobile.add(index);
    }
    this.render();
  }

  onKeydown(event) {
    // Arrow-key roving applies to the tab strip only. In accordion mode each
    // trigger is an independent button and arrows should scroll the page.
    if (!this.isDesktop) return;

    const deltas = { ArrowRight: 1, ArrowLeft: -1, Home: 'first', End: 'last' };
    const delta = deltas[event.key];
    if (delta === undefined) return;

    event.preventDefault();
    const last = this.triggers.length - 1;
    let next;
    if (delta === 'first') next = 0;
    else if (delta === 'last') next = last;
    else next = (this.selected + delta + this.triggers.length) % this.triggers.length;

    this.selected = next;
    this.render();
    this.triggers[next].focus();
  }

  render() {
    const desktop = this.isDesktop;
    this.classList.toggle('orlant-tabs--desktop', desktop);
    this.setAttribute('role', desktop ? 'tablist' : 'presentation');

    this.triggers.forEach((trigger, i) => {
      const open = desktop ? i === this.selected : this.openOnMobile.has(i);
      if (desktop) {
        trigger.setAttribute('role', 'tab');
        trigger.setAttribute('aria-selected', String(open));
        trigger.removeAttribute('aria-expanded');
        // Roving tabindex: only the selected tab is in the tab order.
        trigger.tabIndex = open ? 0 : -1;
      } else {
        trigger.setAttribute('role', 'button');
        trigger.setAttribute('aria-expanded', String(open));
        trigger.removeAttribute('aria-selected');
        trigger.tabIndex = 0;
      }
      trigger.classList.toggle('orlant-tabs__trigger--active', open);
    });

    this.panels.forEach((panel, i) => {
      const open = desktop ? i === this.selected : this.openOnMobile.has(i);
      panel.setAttribute('role', desktop ? 'tabpanel' : 'region');
      panel.hidden = !open;
      if (desktop && open) panel.tabIndex = 0;
      else panel.removeAttribute('tabindex');
    });
  }
}

if (!customElements.get('orlant-tabs')) {
  customElements.define('orlant-tabs', OrlantTabs);
}
