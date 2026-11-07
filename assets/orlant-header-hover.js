/*
  Desktop header dropdowns open on hover (agency request; GoodLiving's
  "Racks" menu as reference). Builds on Dawn's <header-menu> disclosure:

  - Mouse/trackpad only (hover-capable, fine pointer). Touch keeps Dawn's tap
    to open, tap again to close.
  - A short close delay lets the pointer cross the gap into the panel.
  - With the menu open by hover, a mouse click on the top item goes to its
    page (e.g. Products → all products) instead of closing the menu.
  - Keyboard is unchanged: Enter/Space toggles, Escape and Tab-away close.
*/
(() => {
  const canHover = window.matchMedia('(hover: hover) and (pointer: fine)');
  const CLOSE_DELAY = 180;

  // Drop the panel from the header's bottom edge (its gold hairline), not
  // from the menu item, and size the hover bridge to the gap in between.
  const alignPanel = (details) => {
    const panel = details.querySelector(':scope > .header__submenu');
    const wrapper = document.querySelector('.header-wrapper');
    const item = details.closest('header-menu');
    if (!panel || !wrapper || !item) return;
    const gap = Math.max(0, Math.round(wrapper.getBoundingClientRect().bottom - item.getBoundingClientRect().bottom));
    item.style.setProperty('--orlant-menu-gap', `${gap}px`);
  };

  const setOpen = (details, open) => {
    if (open) alignPanel(details);
    if (details.open === open) return;
    details.open = open;
    const summary = details.querySelector('summary');
    if (summary) summary.setAttribute('aria-expanded', String(open));
  };

  const closeOthers = (current) => {
    document.querySelectorAll('.header__inline-menu header-menu > details[open]').forEach((other) => {
      if (other !== current) setOpen(other, false);
    });
  };

  const wire = (menu) => {
    if (menu.dataset.orlantHover) return;
    menu.dataset.orlantHover = 'true';
    const details = menu.querySelector(':scope > details');
    const summary = details && details.querySelector(':scope > summary');
    if (!details || !summary) return;
    let timer;

    menu.addEventListener('mouseenter', () => {
      if (!canHover.matches) return;
      window.clearTimeout(timer);
      closeOthers(details);
      setOpen(details, true);
      details.dataset.openedByHover = 'true';
    });

    menu.addEventListener('mouseleave', () => {
      if (!canHover.matches) return;
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        setOpen(details, false);
        delete details.dataset.openedByHover;
      }, CLOSE_DELAY);
    });

    // event.detail is 0 for keyboard-triggered clicks, so only real mouse
    // clicks navigate.
    summary.addEventListener('click', (event) => {
      const href = details.dataset.orlantHref;
      if (!canHover.matches || event.detail === 0 || !href || href === '#') return;
      if (details.dataset.openedByHover === 'true') {
        event.preventDefault();
        window.location.href = href;
      }
    });

    details.addEventListener('toggle', () => {
      if (details.open) alignPanel(details);
    });

    details.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape' || !details.open) return;
      setOpen(details, false);
      summary.focus();
    });
  };

  const init = () => document.querySelectorAll('.header__inline-menu header-menu').forEach(wire);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
  // The header can be re-rendered in the theme editor.
  document.addEventListener('shopify:section:load', init);
})();
