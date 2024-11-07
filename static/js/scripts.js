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

function initializeSubscriptionReminder() {
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
            }
        }, 1000); // Show after 1 seconds
    }
}

document.addEventListener('DOMContentLoaded', initializeSubscriptionReminder);

document.addEventListener('DOMContentLoaded', function() {
    const scheduleBtn = document.querySelector('input[name="schedule"]');
    const dateInput = document.querySelector('input[name="publish_date"]');
    const timeInput = document.querySelector('input[name="publish_time"]');

    // Function to toggle date/time fields
    function toggleDateTimeFields() {
        const isSchedule = scheduleBtn === document.activeElement;
        dateInput.required = isSchedule;
        timeInput.required = isSchedule;

        if (isSchedule) {
            dateInput.parentElement.style.display = 'block';
            timeInput.parentElement.style.display = 'block';
        } else {
            dateInput.parentElement.style.display = 'none';
            timeInput.parentElement.style.display = 'none';
        }
    }

    // Initial state
    toggleDateTimeFields();

    // Add event listeners to all submit buttons
    document.querySelectorAll('input[type="submit"]').forEach(btn => {
        btn.addEventListener('click', function() {
            toggleDateTimeFields();
        });
    });
});

// Like button functionality with dynamic update
function likePost(postId) {
    fetch(`/post/${postId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const likeCountElement = document.getElementById(`like-count-${postId}`);
        if (likeCountElement) {
            likeCountElement.textContent = `${data.likes} likes`; // Update the like count dynamically
        }
    })
    .catch(error => console.error('Error:', error));
}

// Attach event listener to like buttons
document.addEventListener('DOMContentLoaded', function() {
    const likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            likePost(postId);
        });
    });
});
