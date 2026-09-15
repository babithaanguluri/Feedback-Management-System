// Interactive Star Rating for Student Feedback Form
document.addEventListener('DOMContentLoaded', function() {
    const starContainer = document.getElementById('star-rating-container');
    const ratingInput = document.getElementById('rating-value');
    const helperText = document.getElementById('rating-helper-text');

    if (!starContainer || !ratingInput) return;

    const stars = starContainer.querySelectorAll('.star-item');
    let currentRating = parseInt(ratingInput.value) || 0;

    function updateStars(rating) {
        stars.forEach(star => {
            const starValue = parseInt(star.getAttribute('data-value'));
            const icon = star.querySelector('i');
            if (starValue <= rating) {
                icon.className = 'bi bi-star-fill text-warning';
            } else {
                icon.className = 'bi bi-star text-secondary';
            }
        });

        if (helperText) {
            if (rating === 0) {
                helperText.textContent = 'Please select a rating';
                helperText.className = 'star-helper-text text-muted';
            } else {
                const labels = ['', 'Poor (1/5)', 'Fair (2/5)', 'Good (3/5)', 'Very Good (4/5)', 'Excellent (5/5)'];
                helperText.textContent = `Selected: ${labels[rating] || rating + ' stars'}`;
                helperText.className = 'star-helper-text text-success fw-medium';
            }
        }
    }

    // Initialize with current value
    updateStars(currentRating);

    stars.forEach(star => {
        star.addEventListener('mouseenter', function() {
            const hoverValue = parseInt(this.getAttribute('data-value'));
            updateStars(hoverValue);
        });

        star.addEventListener('click', function() {
            currentRating = parseInt(this.getAttribute('data-value'));
            ratingInput.value = currentRating;
            updateStars(currentRating);
        });
    });

    starContainer.addEventListener('mouseleave', function() {
        updateStars(currentRating);
    });
});
