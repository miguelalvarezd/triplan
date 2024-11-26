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

document.getElementById('manage-bookings-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const bookingCode = document.getElementById('booking-code').value;

    const response = await fetch(`http://localhost:5000/api/bookings/${bookingCode}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    });

    const data = await response.json();

    if (data.success) {
        const booking = data.booking;
        const tableBody = document.querySelector('#summary-table tbody');
        tableBody.innerHTML = ''; // Clear existing rows

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${booking.id}</td>
            <td>${booking.dni}</td>
            <td>${booking.start_date || 'N/A'}</td>
            <td>${booking.end_date || 'N/A'}</td>
        `;
        tableBody.appendChild(row);
    } else {
        alert(data.message);
    }
});

