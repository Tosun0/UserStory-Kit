// assets/app.js

// ─── 플랫폼 기본 설정 (가이드 md와 동일) — 지우지 마세요 ───
// 진입 효과는 자체 상태 머신 대신 IntersectionObserver로
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => e.target.classList.toggle('is-visible', e.isIntersecting));
}, { threshold: 0.25 });

document.querySelectorAll('.page-section').forEach(el => io.observe(el));


// ▼ 내 스크립트 붙여넣기 ▼
// - 내 파일의 <script> 와 </script> 사이 내용이 있다면 이 아래에 붙여넣으세요. (없으면 비워두세요)
// - 마우스 휠 · 키보드로 페이지를 한 장씩 넘기는 코드가 있으면 빼주세요.
// - 위에서 io 라는 이름을 이미 쓰고 있어요. 붙인 코드에 const io 가 또 있으면 오류가 나니 이름을 바꿔주세요.


// ▲ 여기까지 ▲
