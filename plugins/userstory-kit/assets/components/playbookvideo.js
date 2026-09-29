(() => {
  const root = document.querySelector(".ukvideo");
  const video = root.querySelector("video");
  const start = root.querySelector(".ukvideo-start");
  const playback = root.querySelector(".ukvideo-play");
  const replay = root.querySelector(".ukvideo-replay");
  const volume = root.querySelector(".ukvideo-volume");
  const slider = root.querySelector(".ukvideo-slider");
  const mute = root.querySelector(".ukvideo-mute");
  const error = root.querySelector(".ukvideo-error");
  let hideTimer;

  function update(show = false) {
    clearTimeout(hideTimer);
    playback.hidden = !start.hidden || video.ended;
    replay.hidden = !video.ended;
    volume.hidden = !start.hidden;
    playback.textContent = video.paused ? "▶" : "Ⅱ";
    playback.setAttribute("aria-label", video.paused ? "재생" : "정지");
    playback.classList.toggle("visible", video.paused || show);
    const muted = video.muted || video.volume === 0;
    mute.textContent = muted ? "🔇" : "🔊";
    mute.setAttribute("aria-label", muted ? "소리 켜기" : "음소거");
    mute.setAttribute("aria-pressed", String(muted));
    slider.value = String(video.volume);
    if (!video.paused && show) hideTimer = setTimeout(() => playback.classList.remove("visible"), 1000);
  }

  async function play() {
    error.hidden = true;
    try {
      await video.play();
      start.hidden = true;
      const bounds = root.getBoundingClientRect();
      if (bounds.bottom <= 0 || bounds.top >= window.innerHeight) video.pause();
      update(true);
    } catch {
      error.textContent = "영상을 재생하지 못했습니다. 파일 경로와 재생 형식을 확인해 주세요.";
      error.hidden = false;
      update(true);
    }
  }

  function toggle() {
    if (video.paused) play();
    else video.pause();
  }

  start.addEventListener("click", play);
  playback.addEventListener("click", toggle);
  video.addEventListener("click", toggle);
  replay.addEventListener("click", () => { video.currentTime = 0; play(); });
  root.addEventListener("pointermove", () => { if (start.hidden) update(true); });
  video.addEventListener("play", () => update(true));
  video.addEventListener("pause", () => update(true));
  video.addEventListener("ended", () => update());
  video.addEventListener("volumechange", () => update());
  slider.addEventListener("input", () => {
    video.volume = Number(slider.value);
    video.muted = video.volume === 0;
  });
  mute.addEventListener("click", () => {
    const muted = video.muted || video.volume === 0;
    if (video.volume === 0) video.volume = 1;
    video.muted = !muted;
  });
  new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) video.pause();
  }, { threshold: .25 }).observe(root);
  update();
})();
