// Main JavaScript for College Tournament System

// Wait for document to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Handle form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    if (forms.length > 0) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
            }, false);
        });
    }
    
    // Handle alerts auto-dismissal
    const alerts = document.querySelectorAll('.alert-dismissible.auto-dismiss');
    
    if (alerts.length > 0) {
        Array.from(alerts).forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000); // Auto dismiss after 5 seconds
        });
    }
    
    // Handle tournament type selection in create tournament form
    const tournamentTypeSelect = document.getElementById('tournament_type');
    const descriptionField = document.getElementById('description');
    
    if (tournamentTypeSelect && descriptionField) {
        tournamentTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            let defaultDescription = '';
            
            switch(selectedType) {
                case 'TABLE_TENNIS':
                    defaultDescription = 'Table Tennis tournament with matches played as best of 3, 5, or 7 sets. Each set is played to 11 points with a 2-point advantage required.';
                    break;
                case 'FOOTBALL':
                    defaultDescription = 'Football tournament with 5-a-side teams. Matches are 90 minutes long. Win: 3 points, Draw: 1 point, Loss: 0 points.';
                    break;
                case 'MATH_QUIZ':
                    defaultDescription = 'Mathematics Quiz competition with 10 questions per round. Each correct answer is worth 10 points. Best total score wins.';
                    break;
                default:
                    defaultDescription = 'Tournament description...';
            }
            
            if (!descriptionField.value) {
                descriptionField.value = defaultDescription;
            }
        });
    }
});

// Function to confirm deletion
function confirmDelete(message, formId) {
    if (confirm(message || 'Are you sure you want to delete this item?')) {
        document.getElementById(formId).submit();
    }
    return false;
}

// Function to handle error responses
function handleApiError(error) {
    console.error('API Error:', error);
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = error.message || 'An error occurred. Please try again.';
        errorDiv.classList.remove('d-none');
        setTimeout(() => {
            errorDiv.classList.add('d-none');
        }, 5000);
    }
}
