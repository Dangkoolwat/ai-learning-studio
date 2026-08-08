export function initImageLightbox() {
  // Now we only query images that have been wrapped by the renderer
  const images = document.querySelectorAll('.image-wrapper.lightbox-enabled img');
  if (images.length === 0) return;

  const dialog = document.createElement('dialog');
  dialog.className = 'image-lightbox';
  dialog.innerHTML = `
    <div class="lightbox-content">
      <button type="button" class="lightbox-close" aria-label="닫기" title="닫기">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
      <img src="" alt="" class="lightbox-img">
      <a href="" download class="lightbox-download" aria-label="다운로드" title="원본 다운로드">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        다운로드
      </a>
    </div>
  `;
  document.body.appendChild(dialog);

  const imgEl = dialog.querySelector('.lightbox-img');
  const downloadBtn = dialog.querySelector('.lightbox-download');
  const closeBtn = dialog.querySelector('.lightbox-close');

  function closeLightbox() {
    dialog.close();
  }

  closeBtn.addEventListener('click', closeLightbox);

  // Close when clicking on backdrop or outside image
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog || e.target.classList.contains('lightbox-content')) {
      closeLightbox();
    }
  });

  images.forEach(img => {
    img.addEventListener('click', () => {
      imgEl.src = img.src;
      imgEl.alt = img.alt || '확대된 이미지';
      downloadBtn.href = img.src;
      
      let filename = img.src.split('/').pop().split('#')[0].split('?')[0];
      if (!filename) filename = 'download';
      downloadBtn.download = filename;
      
      dialog.showModal();
    });
  });
}
