function scrollToLogin() {
    document.getElementById('admin-login').scrollIntoView({ behavior: 'smooth' });
}

function goToSplash() {
    document.getElementById('splash-section').scrollIntoView({ behavior: 'smooth' });
}

// Get the elements
const employeeForm = document.getElementById('employee');
const adminForm = document.getElementById('admin');

// Function to handle employee label click
function showEmployeeForm() {
    employeeForm.style.zIndex = 2;         
    adminForm.style.zIndex = 1;        
    employeeForm.style.pointerEvents = 'auto';
}

// Function to handle admin label click
function showAdminForm() {
    adminForm.style.zIndex = 2;        
    employeeForm.style.zIndex = 1;     
    adminForm.style.pointerEvents = 'auto';
}
