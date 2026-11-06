/*
  Function block videos: play muted and looped only while on screen, so
  off-screen rows cost no bandwidth or battery. With reduced motion requested
  the video never plays and its poster (the block image) stays.
*/
if (!customElements.get('orlant-autoplay-video')) {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  customElements.define(
    'orlant-autoplay-video',
    class extends HTMLElement {
      connectedCallback() {
        this.video = this.querySelector('video');
        if (!this.video || reduce.matches || !('IntersectionObserver' in window)) return;
        this.observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                const attempt = this.video.play();
                if (attempt && attempt.catch) attempt.catch(() => {});
              } else {
                this.video.pause();
              }
            });
          },
          { threshold: 0.35 }
        );
        this.observer.observe(this);
      }

      disconnectedCallback() {
        if (this.observer) this.observer.disconnect();
      }
    }
  );
}
