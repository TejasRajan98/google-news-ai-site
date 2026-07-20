document.addEventListener('DOMContentLoaded', () => {
  // Select DOM Elements
  const newsContainer = document.getElementById('news-container');
  const filterButtons = document.querySelectorAll('.filter-btn');
  const contactForm = document.getElementById('contact-form');
  const successMessage = document.getElementById('success-message');
  
  // Modal Elements
  const modal = document.getElementById('news-modal');
  const modalClose = document.getElementById('modal-close');
  const modalImg = document.getElementById('modal-img');
  const modalCategory = document.getElementById('modal-category');
  const modalDate = document.getElementById('modal-date');
  const modalReadTime = document.getElementById('modal-read-time');
  const modalTitle = document.getElementById('modal-title');
  const modalDesc = document.getElementById('modal-desc');
  const modalLink = document.getElementById('modal-link');

  let currentCategory = 'all';

  // 1. Fetch and Render News
  async function fetchNews(category = 'all') {
    if (!newsContainer) return;
    
    // Show Loading Spinner
    newsContainer.innerHTML = `
      <div class="loading-container">
        <div class="spinner"></div>
      </div>
    `;

    try {
      const url = category === 'all' ? `/api/news?_=${Date.now()}` : `/api/news?category=${encodeURIComponent(category)}&_=${Date.now()}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to load news');
      const newsItems = await response.json();
      
      renderNews(newsItems);
    } catch (error) {
      console.error(error);
      newsContainer.innerHTML = `
        <div class="loading-container">
          <p style="color: var(--google-red); font-weight: 500;">Failed to load news articles. Please try again later.</p>
        </div>
      `;
    }
  }

  function renderNews(articles) {
    if (articles.length === 0) {
      newsContainer.innerHTML = `
        <div class="loading-container">
          <p style="color: var(--text-secondary);">No articles found in this category.</p>
        </div>
      `;
      return;
    }

    newsContainer.innerHTML = articles.map(article => {
      // Create initial avatar initial
      const initial = article.author ? article.author.charAt(0) : 'G';
      
      return `
        <article class="news-card" data-id="${article.id}">
          <div class="card-img-wrapper">
            <span class="card-category">${article.category}</span>
            <img class="card-img" src="${article.image_url}" alt="${article.title}" loading="lazy">
          </div>
          <div class="card-content">
            <div class="card-meta">
              <span>${article.date}</span>
              <span>${article.read_time}</span>
            </div>
            <h3 class="card-title">${article.title}</h3>
            <p class="card-snippet">${article.snippet}</p>
            <div class="card-footer">
              <div class="author-info">
                <div class="author-avatar">${initial}</div>
                <span class="author-name">${article.author}</span>
              </div>
              <a href="#" class="read-more-btn" data-id="${article.id}">
                Read More 
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </a>
            </div>
          </div>
        </article>
      `;
    }).join('');

    // Attach Event Listeners to Read More buttons & Cards
    const readMoreBtns = newsContainer.querySelectorAll('.read-more-btn');
    readMoreBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const articleId = parseInt(btn.getAttribute('data-id'));
        openArticleModal(articleId, articles);
      });
    });
  }

  // 2. Open Article Modal
  function openArticleModal(id, articles) {
    if (!modal) return;
    
    const article = articles.find(a => a.id === id);
    if (!article) return;

    modalImg.src = article.image_url;
    modalImg.alt = article.title;
    modalCategory.textContent = article.category;
    modalDate.textContent = article.date;
    modalReadTime.textContent = article.read_time;
    modalTitle.textContent = article.title;
    modalDesc.textContent = article.content;
    if (modalLink) {
      modalLink.href = article.link;
    }

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Disable page scrolling
  }

  // Close Modal
  if (modalClose) {
    modalClose.addEventListener('click', () => {
      modal.style.display = 'none';
      document.body.style.overflow = 'auto'; // Enable page scrolling
    });
  }

  // Close Modal on clicking backdrop
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
      }
    });
  }

  // 3. Category Filter buttons
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      // Toggle Active Class
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      currentCategory = btn.getAttribute('data-category');
      fetchNews(currentCategory);
    });
  });

  // 4. Contact Form Handling
  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const submitBtn = contactForm.querySelector('.submit-btn');
      const originalText = submitBtn.innerHTML;

      // Visual feedback loading state
      submitBtn.innerHTML = 'Sending...';
      submitBtn.disabled = true;

      // Simulate API submit delay
      setTimeout(() => {
        // Reset form & show success
        contactForm.reset();
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
        successMessage.style.display = 'block';
        
        // Hide message after 5 seconds
        setTimeout(() => {
          successMessage.style.display = 'none';
        }, 5000);
      }, 1000);
    });
  }

  // Initial Fetch
  fetchNews();
});
