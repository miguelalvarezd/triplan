// CLIENT PORTAL SCRIPTS
// alert("scripts.js is loaded!");

document.addEventListener('DOMContentLoaded', async () => {
    // Identify the current page based on unique elements
    const welcomeMessage = document.getElementById('welcome-message');
    const clientInfoModal = document.getElementById('clientInfoModal');
    const bookingTable = document.getElementById('summary-table');

    // For client-portal.html
    if (welcomeMessage && clientInfoModal && bookingTable) {
        // Update the welcome message with the client's name
        const customerName = localStorage.getItem('customerName');
        if (customerName) {
            welcomeMessage.textContent = `Welcome, ${customerName}!`;
        }

        // Setup the "Show Client Data" button functionality
        window.openClientInfoModal = async () => {
            const dni = localStorage.getItem('customerDNI');
            if (!dni) return alert("No client information found.");

            try {
                const response = await fetch(`http://localhost:5000/api/customers/${dni}`);
                const data = await response.json();
                
                if (data.success) {
                    const tableBody = document.querySelector('#modal-client-table tbody');
                    tableBody.innerHTML = ''; // Clear previous rows
                    const client = data.customer;
                    const row = `
                        <tr>
                            <td>${client.dni}</td>
                            <td>${client.name}</td>
                            <td>${client.phone || 'N/A'}</td>
                            <td>${client.tier || 'N/A'}</td>
                        </tr>`;
                    tableBody.innerHTML = row;
                    clientInfoModal.style.display = 'block';
                } else {
                    alert(data.message);
                }
            } catch (error) {
                console.error("Error fetching client data:", error);
                alert("Failed to load client data. Please try again.");
            }
        };

        // Close the modal
        window.closeClientInfoModal = () => {
            clientInfoModal.style.display = 'none';
        };

        async function populateBookingSummary() {
            const dni = localStorage.getItem('customerDNI');
            const summaryTable = document.getElementById('summary-table');
            const noBookingsMessage = document.getElementById('no-bookings-message');
            
            if (!dni) {
                console.error("No DNI found in localStorage");
                return;
            }
        
            if (!summaryTable) {
                console.error("Summary table element not found");
                return;
            }
        
            try {
                // Updated endpoint URL
                const response = await fetch(`http://localhost:5000/api/bookings/client/${dni}`);
                const data = await response.json();
                console.log('Booking data received:', data);
        
                const tableBody = summaryTable.querySelector('tbody');
                if (!tableBody) {
                    console.error("Table body not found");
                    return;
                }
        
                // Clear existing rows
                tableBody.innerHTML = '';
        
                if (data.success && data.bookings && data.bookings.length > 0) {
                    data.bookings.forEach(booking => {
                        const row = document.createElement('tr');
                        // Format dates if they exist
                        const startDate = booking.start_date ? new Date(booking.start_date).toLocaleDateString() : 'N/A';
                        const endDate = booking.end_date ? new Date(booking.end_date).toLocaleDateString() : 'N/A';
                        
                        row.innerHTML = `
                            <td>${booking.id}</td>
                            <td>${booking.dni}</td>
                            <td>${startDate}</td>
                            <td>${endDate}</td>
                        `;
                        tableBody.appendChild(row);
                    });
                    summaryTable.style.display = 'table';
                    noBookingsMessage.style.display = 'none';
                } else {
                    summaryTable.style.display = 'none';
                    noBookingsMessage.style.display = 'block';
                }
            } catch (error) {
                console.error("Error fetching bookings:", error);
                summaryTable.style.display = 'none';
                noBookingsMessage.style.display = 'block';
                noBookingsMessage.textContent = 'Error loading bookings. Please try again later.';
            }
        }
        
        // Ensure this is called when the page loads
        if (document.getElementById('booking-summary')) {
            populateBookingSummary();
        }
    }
});

document.getElementById('new-customer-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const dni = document.getElementById('dni').value;
    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;

    const response = await fetch('http://localhost:5000/api/customers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dni, name, phone })
    });

    const data = await response.json();
    alert(data.message);
});

document.getElementById('returning-customer-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const dni = document.getElementById('dni-return').value;

    const response = await fetch(`http://localhost:5000/api/customers/${dni}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    });

    const data = await response.json();
    if (data.success) {
        const customer = data.customer;
        const tableBody = document.querySelector('#customer-table tbody');
        tableBody.innerHTML = ''; // Clear existing rows

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${customer.dni}</td>
            <td>${customer.name}</td>
            <td>${customer.phone || 'N/A'}</td>
            <td>${customer.tier || 'N/A'}</td>
        `;
        tableBody.appendChild(row);
    } else {
        alert(data.message);
    }
});

document.getElementById('booking-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const bookingDetails = {
        origin: document.getElementById('origin').value,
        destination: document.getElementById('destination').value,
        flightDate: document.getElementById('flight-date').value,
        seatClass: document.getElementById('seat-class').value,
        seatNumber: document.getElementById('seat-number').value,
        hotel: document.getElementById('hotel').value,
        roomType: document.getElementById('room-type').value,
        carModel: document.getElementById('car-model').value,
        seats: document.getElementById('seats').value
    };

    const response = await fetch('http://localhost:5000/api/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookingDetails)
    });

    const data = await response.json();
    alert(data.message);
});

function manageBookings(event) {
    event.preventDefault();

    const bookingCode = document.getElementById('booking-code').value;
    const summaryTable = document.getElementById('summary-table-2');
    const tableBody = summaryTable.querySelector('tbody');
    const noBookingsMessage = document.getElementById('no-bookings-message-2');

    fetch(`http://localhost:5000/api/bookings/code/${bookingCode}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.booking) {
            const booking = data.booking;
            tableBody.innerHTML = ''; // Clear existing rows

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${booking.id}</td>
                <td>${booking.dni}</td>
                <td>${booking.start_date || 'N/A'}</td>
                <td>${booking.end_date || 'N/A'}</td>
            `;
            tableBody.appendChild(row);

            // Show table and hide "no bookings" message
            summaryTable.style.display = 'table'; // Use 'table' to properly display the element
            noBookingsMessage.style.display = 'none';
        } else {
            // Hide table and show "no bookings" message
            summaryTable.style.display = 'none';
            noBookingsMessage.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while searching for the booking.');
    });
}

// LANDING PAGE SCRIPTS

// Modal functionality
function openClientModal() {
    document.getElementById('clientModal').style.display = 'block';
}

function closeClientModal() {
    document.getElementById('clientModal').style.display = 'none';
    document.getElementById('loginForm').reset();
    document.getElementById('newClientForm').reset();
    document.getElementById('loginSuccess').style.display = 'none';
    document.getElementById('loginFailed').style.display = 'none';
    document.getElementById('registrationSuccess').style.display = 'none';
    document.getElementById('registrationFailed').style.display = 'none';

}

// Handle login form submission
function handleLogin(event) {
    event.preventDefault();

    document.getElementById('loginSuccess').style.display = 'none';
    document.getElementById('loginFailed').style.display = 'none';
    
    const dni = document.getElementById('username').value;
    const phone = document.getElementById('password').value;

    fetch('http://localhost:5000/api/customers/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dni, phone })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            localStorage.setItem('customerDNI', data.dni);
            localStorage.setItem('customerName', data.name);
            //alert(`Welcome, ${data.name}!`);
            document.getElementById('loginSuccess').style.display = 'block';
            setTimeout(() => {
                closeClientModal();
                // Store login state (in a real app, you'd use proper authentication)
                localStorage.setItem('isLoggedIn', 'true');
                // Redirect to client portal
                window.location.href = 'static/client-portal.html';
            }, 1000);
            
        } else {
            document.getElementById('loginFailed').style.display = 'block';
            //alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during login. Please try again.');
    });
}

// Handle new client registration
function handleNewClient(event) {
    event.preventDefault();

    document.getElementById('registrationSuccess').style.display = 'none';
    document.getElementById('registrationFailed').style.display = 'none';

    
    const dni = document.getElementById('dni').value;
    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;

    fetch('http://localhost:5000/api/customers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dni, name, phone })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Info:', data);
        if (data.success) {
            //localStorage.setItem('customerDNI', data.dni);
            // localStorage.setItem('customerName', data.name);
            //alert(`Welcome, ${data.name}!`);
            localStorage.setItem('customerDNI', dni);
            localStorage.setItem('customerName', name);

            document.getElementById('registrationSuccess').style.display = 'block';

            setTimeout(() => {
                closeClientModal();
                // Store login state (in a real app, you'd use proper authentication)
                localStorage.setItem('isLoggedIn', 'true');
                // Redirect to client portal
                window.location.href = 'static/client-portal.html';
            }, 1000);
            console.log('Info:', data);
            
        } else {
            document.getElementById('registrationFailed').style.display = 'block';
            //alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during login. Please try again.');
    });
}

function openAgentPortal() {
    alert('Agent portal is under development.');
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target == document.getElementById('clientModal')) {
        closeClientModal();
    }
}

function logout() {
    if (confirm("Are you sure you want to logout?")) {
        // Clear client info from localStorage
        localStorage.removeItem('customerDNI');
        localStorage.removeItem('customerName');

        // Redirect to the login page
        window.location.href = 'http://localhost:5000/';
    }
}

