class ImageUploader {
  constructor(wrapper) {
      this.wrapper = wrapper;
      this.fileInput = wrapper.querySelector('.image-file-input');
      this.urlInput = wrapper.querySelector('.url-input');
      this.previewImg = wrapper.querySelector('.preview-image');
      this.localBtn = wrapper.querySelector('.upload-local-btn');
      this.ossBtn = wrapper.querySelector('.upload-oss-btn');
      

      this.bindEvents();
      this.initialize();
  }

  initialize() {
      if (this.urlInput.value) {
          this.previewImg.src = this.urlInput.value;
          this.previewImg.style.display = 'block';
      }
  }

  bindEvents() {
      // 本地按钮
      this.localBtn.addEventListener('click', (e) => {
          e.preventDefault();
          this.fileInput.click();
      });

      // 文件选择
      this.fileInput.addEventListener('change', (e) => {
          const file = e.target.files[0];
          if (!file) return;
          
          const reader = new FileReader();
          reader.onload = (e) => {
              this.previewImg.src = e.target.result;
              this.previewImg.style.display = 'block';
          };
          reader.readAsDataURL(file);
      });

      // OSS上传
      this.ossBtn.addEventListener('click', async (e) => {
          e.preventDefault();
          const file = this.fileInput.files[0];
          if (!file) {
              return alert('请先选择文件');
          }

          this.ossBtn.disabled = true;
          this.ossBtn.textContent = '上传中...';
          
          try {
              const formData = new FormData();
              formData.append('image', file);
              
              const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
              const response = await fetch(this.wrapper.querySelector('.upload-url').value, {
                  method: 'POST',
                  body: formData,
                  headers: { 
                      'X-CSRFToken': csrfToken,
                      'Accept': 'application/json'
                  }
              });

              if (!response.ok) throw new Error(`HTTP错误 ${response.status}`);
              const data = await response.json();
              
              if (data.url) {
                  this.urlInput.value = data.url;
                  this.previewImg.src = data.url;
              }
          } catch (error) {
              alert(`上传失败: ${error.message}`);
          } finally {
              this.ossBtn.disabled = false;
              this.ossBtn.textContent = '上传到云存储';
          }
      });

      // URL输入监控
      this.urlInput.addEventListener('input', () => {
          this.previewImg.src = this.urlInput.value;
      });

      // 图片加载监控
      this.previewImg.addEventListener('load', () => {
          this.previewImg.style.display = 'block';
      });
      
      this.previewImg.addEventListener('error', () => {
          this.previewImg.style.display = 'none';
      });
  }
}

// 安全初始化
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.image-upload-wrapper').forEach(wrapper => {
      try {
          new ImageUploader(wrapper);
      } catch (error) {
        alert('初始化失败:', error);
      }
  });
});
