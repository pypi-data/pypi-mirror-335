document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission

            // Get form values
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();

            // Basic input validation
            if (!username || !password) {
                showAlert('Please fill out all fields.', 'error');
                return;
            }

            // Successful validation message
            showAlert(`Logging in with username: ${username}`, 'success');

            // TODO: Implement form submission logic (e.g., AJAX request)
        });
    }

    // Function to show alert messages
    function showAlert(message, type) {
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) existingAlert.remove(); // Remove existing alerts

        const alert = document.createElement('div');
        alert.className = `alert ${type}`;
        alert.textContent = message;

        // Insert alert message above the form
        loginForm.parentNode.insertBefore(alert, loginForm);

        // Automatically remove alert after 3 seconds
        setTimeout(() => {
            if (alert) alert.remove();
        }, 3000);
    }
});
