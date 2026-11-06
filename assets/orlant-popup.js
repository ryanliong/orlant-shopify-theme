/*
  Mailing list pop-up — see snippets/orlant-newsletter-popup.liquid.
  Storage can be blocked (private windows, strict settings); every read and
  write is guarded, and without storage the pop-up simply shows once per page
  view at most.
*/
if (!customElements.get('orlant-popup')) {
  const KEY_SUBSCRIBED = 'orlant-popup-subscribed';
  const KEY_SNOOZE = 'orlant-popup-snooze-until';
  const KEY_SUBMITTED = 'orlant-popup-submitted';

  const store = {
    get(area, key) {
      try { return window[area].getItem(key); } catch (e) { return null; }
    },
    set(area, key, value) {
      try { window[area].setItem(key, value); } catch (e) { /* storage blocked */ }
    },
    remove(area, key) {
      try { window[area].removeItem(key); } catch (e) { /* storage blocked */ }
    },
  };

  customElements.define(
    'orlant-popup',
    class extends HTMLElement {
      connectedCallback() {
        this.dialog = this.querySelector('dialog');
        if (!this.dialog || typeof this.dialog.showModal !== 'function') return;

        this.delay = (parseInt(this.dataset.delay, 10) || 10) * 1000;
        this.snoozeDays = parseInt(this.dataset.snoozeDays, 10) || 30;
        this.opened = false;

        this.querySelectorAll('[data-popup-close]').forEach((btn) =>
          btn.addEventListener('click', () => this.close())
        );
        // Escape fires "cancel"; treat it like the close button.
        this.dialog.addEventListener('cancel', (event) => {
          event.preventDefault();
          this.close();
        });
        // A click on the backdrop lands on the dialog element itself.
        this.dialog.addEventListener('click', (event) => {
          if (event.target === this.dialog) this.close();
        });
        const form = this.querySelector('form');
        if (form) form.addEventListener('submit', () => store.set('sessionStorage', KEY_SUBMITTED, '1'));

        // Back from a submission: Shopify reloads the page. Reopen only if the
        // submission came from this pop-up (the footer form posts the same way).
        const submittedHere = store.get('sessionStorage', KEY_SUBMITTED) === '1';
        const params = new URLSearchParams(window.location.search);
        const success = this.querySelector('[data-popup-state="success"]');
        const error = this.querySelector('[data-popup-state="error"]');

        if (params.get('customer_posted') === 'true' || success) {
          store.set('localStorage', KEY_SUBSCRIBED, '1');
        }
        if (submittedHere && (success || error)) {
          store.remove('sessionStorage', KEY_SUBMITTED);
          this.open();
          return;
        }

        if (store.get('localStorage', KEY_SUBSCRIBED) === '1') return;
        const snoozeUntil = parseInt(store.get('localStorage', KEY_SNOOZE), 10);
        if (snoozeUntil && Date.now() < snoozeUntil) return;
        if ((params.get('utm_medium') || '').toLowerCase() === 'email') return;
        if (window.Shopify && window.Shopify.designMode) return;

        this.timer = window.setTimeout(() => this.tryOpen(), this.delay);
        this.onScroll = () => {
          const doc = document.documentElement;
          const scrollable = doc.scrollHeight - window.innerHeight;
          if (scrollable > 0 && window.scrollY / scrollable >= 0.5) this.tryOpen();
        };
        window.addEventListener('scroll', this.onScroll, { passive: true });
      }

      disconnectedCallback() {
        window.clearTimeout(this.timer);
        if (this.onScroll) window.removeEventListener('scroll', this.onScroll);
      }

      // Never on top of the cart drawer, menu or another modal; try again later.
      tryOpen() {
        if (this.opened) return;
        if (/\boverflow-hidden/.test(document.body.className) || document.querySelector('dialog[open]')) {
          window.clearTimeout(this.timer);
          this.timer = window.setTimeout(() => this.tryOpen(), 5000);
          return;
        }
        this.open();
      }

      open() {
        if (this.opened) return;
        this.opened = true;
        window.clearTimeout(this.timer);
        if (this.onScroll) window.removeEventListener('scroll', this.onScroll);
        this.previousFocus = document.activeElement;
        this.dialog.showModal();
        const field = this.dialog.querySelector('input[type="email"]');
        (field || this.dialog.querySelector('[data-popup-close]')).focus();
      }

      close() {
        if (!this.dialog.open) return;
        this.dialog.close();
        const until = Date.now() + this.snoozeDays * 24 * 60 * 60 * 1000;
        store.set('localStorage', KEY_SNOOZE, String(until));
        if (this.previousFocus && this.previousFocus.focus) this.previousFocus.focus();
      }
    }
  );
}
