document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('menu-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('sidebar').classList.toggle('toggled');
        });
    }

    const autoAlerts = document.querySelectorAll('.alert-dismissible');
    autoAlerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
