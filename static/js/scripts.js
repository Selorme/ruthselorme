console.log("JavaScript file loaded");

window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav ? mainNav.clientHeight : 0;

    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if (currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else if (mainNav) {
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            if (mainNav) {
                mainNav.classList.remove('is-visible');
                if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                    mainNav.classList.add('is-fixed');
                }
            }
        }
        scrollPos = currentTop;
    });

    // Theme toggle functionality
    const darkModeToggle = document.getElementById('darkModeToggle');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (darkModeToggle) {
            darkModeToggle.checked = true;
        }
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', () => {
            if (darkModeToggle.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }
        });
    }

    // Reply form toggle
    window.toggleReplyForm = function(commentId) {
        const replyForm = document.getElementById('replyForm' + commentId);
        if (replyForm) {
            replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
        }
    };

    // Subscription reminder
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
            }, 1000); // Show after 1 second
        }
    }
    initializeSubscriptionReminder();

    // Schedule toggle functionality
    const scheduleBtn = document.querySelector('input[name="schedule"]');
    const dateInput = document.querySelector('input[name="publish_date"]');
    const timeInput = document.querySelector('input[name="publish_time"]');

    function toggleDateTimeFields() {
        // Ensure elements exist before accessing properties
        if (scheduleBtn && dateInput && timeInput) {
            const isSchedule = scheduleBtn === document.activeElement;
            dateInput.required = isSchedule;
            timeInput.required = isSchedule;

            dateInput.parentElement.style.display = isSchedule ? 'block' : 'none';
            timeInput.parentElement.style.display = isSchedule ? 'block' : 'none';
        }
    }

    // Initial state
    toggleDateTimeFields();

    // Event listeners for submit buttons
    document.querySelectorAll('input[type="submit"]').forEach(btn => {
        btn.addEventListener('click', toggleDateTimeFields);
    });

    // Initialize CKEditor with upload functionality
    const editorContainer = document.getElementById("editor-container");
    const uploadUrl = editorContainer ? editorContainer.getAttribute("data-upload-url") : '';

    CKEDITOR.replace('body', {
        extraPlugins: 'uploadimage',
        filebrowserUploadUrl: uploadUrl,
        filebrowserUploadMethod: 'form',
        contentsCss: ['/static/css/ckeditor_custom.css'],
        on: {
            instanceReady: function(evt) {
                const editor = evt.editor;
                editor.document.on('drop', function(event) {
                    setTimeout(() => {
                        const images = editor.document.getBody().find('img');
                        images.forEach(img => {
                            img.addClass('img-fluid'); // Add img-fluid class to images
                        });
                    }, 100);
                });
            }
        }
    });
});
