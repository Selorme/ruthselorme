console.log("JavaScript file loaded");
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;

    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if (currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove('is-visible');
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
});

// Theme toggle functionality
document.addEventListener('DOMContentLoaded', () => {
  const darkModeToggle = document.getElementById('darkModeToggle');
  const currentTheme = localStorage.getItem('theme');

  if (currentTheme === 'dark') {
    document.body.classList.add('dark-mode');
    darkModeToggle.checked = true;
  }

  darkModeToggle.addEventListener('change', () => {
    if (darkModeToggle.checked) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
    }
  });
});

    function toggleReplyForm(commentId) {
        const replyForm = document.getElementById('replyForm' + commentId);
        if (replyForm.style.display === 'none') {
            replyForm.style.display = 'block';
        } else {
            replyForm.style.display = 'none';
        }
    }

// In your external JS file
function initializeSubscriptionReminder() {
    if (!localStorage.getItem('subscription_reminder_shown')) {
        const isLoggedIn = document.body.getAttribute('data-user-authenticated') === 'true';

        if (!isLoggedIn) {
            setTimeout(() => {
                const flashContainer = document.querySelector('.flash-messages');
                if (flashContainer) {
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-info alert-dismissible fade show';
                    alert.innerHTML = `
                        <strong>Stay Updated!</strong> Register to receive notifications about new blog posts.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    flashContainer.appendChild(alert);

                    // Set reminder shown flag
                    localStorage.setItem('subscription_reminder_shown', 'true');

                    // Reset flag after 24 hours
                    setTimeout(() => {
                        localStorage.removeItem('subscription_reminder_shown');
                    }, 24 * 60 * 60 * 1000);
                }
            }, 30000); // Show after 30 seconds
        }
    }
}

// Add this to your existing document.ready or window.onload handler
document.addEventListener('DOMContentLoaded', initializeSubscriptionReminder);