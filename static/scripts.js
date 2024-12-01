// CLIENT PORTAL SCRIPTS
let currentRouteID = null;
let currentFlightDestination = null; // Global variable to store the destination
let selectedHotelID = null;
let selectedCarID = null;

const bookFlightModal = document.getElementById('bookFlightModal');

document.addEventListener('DOMContentLoaded', async () => {
    // Identify the current page based on unique elements
    const welcomeMessage = document.getElementById('welcome-message');
    const clientInfoModal = document.getElementById('clientInfoModal');
    const bookingTable = document.getElementById('summary-table');

    if (bookFlightModal) {
        bookFlightModal.style.display = 'none'; // Ensure modal is hidden initially
    }

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
        
        // Ensure this is called when the page loads
        if (document.getElementById('booking-summary')) {
            populateBookingSummary();
        }
    }

    const header = document.querySelector('.portal-user');
    if (!header) {
        console.error('Header element not found');
        return;
    }

    let lastScrollY = window.scrollY;

    window.addEventListener('scroll', () => {
        if (window.scrollY === 0) {
            header.classList.remove('hidden'); // Siempre visible en la parte superior
        } else if (window.scrollY > lastScrollY) {
            header.classList.add('hidden');
        } else {
            header.classList.remove('hidden');
        }
        lastScrollY = window.scrollY;
    });
    

    const portalContainer = document.querySelector('.portal-container');

    if (header && portalContainer) {
        // Adjust the margin based on the header height
        const adjustContentMargin = () => {
            const headerHeight = header.offsetHeight;
            portalContainer.style.marginTop = `${headerHeight}px`;
        };

        // Initial adjustment
        adjustContentMargin();

        // Re-adjust if the window resizes
        window.addEventListener('resize', adjustContentMargin);
    } else {
        console.error('Header or portal container not found.');
    }

    const tiersTable = document.getElementById('tiers-table');
    const tableBody = tiersTable?.querySelector('tbody');
    const editDiscountModal = document.getElementById('editDiscountModal');
    const modalTierName = document.getElementById('modal-tier-name');
    const editDiscountForm = document.getElementById('edit-discount-form');
    let currentTier = null;

    // Function to fetch and populate the tiers table
    async function populateTiersTable() {
        if (!tiersTable || !tableBody) {
            console.error('Tiers table or its body not found.');
            return;
        }

        // Clear existing rows
        tableBody.innerHTML = '';

        try {
            const response = await fetch(`http://localhost:5000/api/tiers`);
            const data = await response.json();

            if (data.success && data.tiers) {
                data.tiers.forEach(tier => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${tier.tier}</td>
                        <td>${tier.descuento}%</td>
                        <td>
                            <button id='edit-tier' onclick="openEditDiscountModal('${tier.tier}', '${tier.descuento}')">Edit Discount</button>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });

                tiersTable.style.display = 'table';
            } else {
                console.warn('No tiers data found or the response was not successful.');
                tiersTable.style.display = 'none';
            }
        } catch (error) {
            console.error('Error fetching tiers:', error);
        }
    }

    // Open the edit discount modal
    window.openEditDiscountModal = (tier, discount) => {
        currentTier = tier;
        modalTierName.textContent = tier;
        // document.getElementById('new-discount').value = discount;
        editDiscountModal.style.display = 'block';
    };

    // Close the modal
    window.closeEditDiscountModal = () => {
        currentTier = null;
        editDiscountModal.style.display = 'none';
        document.getElementById('edit-discount-form').reset();
        document.getElementById('edit-tiers-success').style.display = 'none';
        document.getElementById('edit-tiers-fail').style.display = 'none';
    };

    // Handle the form submission
    editDiscountForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const newDiscount = document.getElementById('new-discount').value;

        if (!currentTier) {
            alert('No tier selected for editing.');
            return;
        }

        try {
            const response = await fetch(`http://localhost:5000/api/tiers`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tier: currentTier, discount: newDiscount })
            });
            const data = await response.json();

            if (data.success) {
                // alert(`Discount for ${currentTier} updated successfully!`);
                document.getElementById('edit-tiers-fail').style.display = 'none';
                document.getElementById('edit-tiers-success').style.display = 'block';
                populateTiersTable(); // Refresh the table

                setTimeout(() => {
                    window.closeEditDiscountModal();
                }, 1000);
            } else {
                // alert(data.message || 'Failed to update discount.');
                document.getElementById('edit-tiers-fail').style.display = 'block';
            }
        } catch (error) {
            console.error('Error updating discount:', error);
            alert('An error occurred while updating the discount.');
        }
    });

    // Call the populate function on page load
    if (tiersTable) {
        populateTiersTable();
    }
});

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
                    <td style='text-align: center;'>
                        <div class='booking-actions'>
                            <button id='booking-details' onclick="openBookingDetailsModal('${booking.id}')">Show Details</button>
                            <button id='cancel-booking' onclick="openCancelBookingModal('${booking.id}')">Cancel Booking</button>
                        </div>
                    </td>
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

const cancelBookingModal = document.getElementById('cancelBookingModal');
const modalBookingID = document.getElementById('modal-booking-id');

async function cancelBooking() {
    try {
        if (!currentBookingID) {
            alert('No booking ID provided.');
            return;
        }

        const response = await fetch(`http://localhost:5000/api/bookings/cancel/${currentBookingID}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('cancel-booking-fail').style.display = 'none'; // Hide any previous errors
            document.getElementById('cancel-booking-success').textContent = data.message || 'Booking cancelled successfully!';
            document.getElementById('cancel-booking-success').style.display = 'block';
            populateBookingSummary(); // Refresh the booking table

            setTimeout(() => {
                window.closeCancelBookingModal();
            }, 1000);
        } else {
            // Display the error message from the API
            document.getElementById('cancel-booking-fail').textContent = data.message || 'Failed to cancel booking.';
            document.getElementById('cancel-booking-fail').style.display = 'block';
        }
    } catch (error) {
        console.error('Error canceling booking:', error);
        document.getElementById('cancel-booking-fail').textContent = 'An error occurred while cancelling the booking. Please try again later.';
        document.getElementById('cancel-booking-fail').style.display = 'block';
    }
}

window.openCancelBookingModal = (bookingID) => {
    currentBookingID = bookingID;
    modalBookingID.textContent = bookingID;
    cancelBookingModal.style.display = 'block';
};

// Close the modal
window.closeCancelBookingModal = () => {
    cancelBookingModal.style.display = 'none';
    document.getElementById('cancel-booking-success').style.display = 'none';
    document.getElementById('cancel-booking-fail').style.display = 'none';
};

// Open Booking Details Modal
function openBookingDetailsModal(bookingID) {
    document.getElementById('details-booking-id').textContent = bookingID;
    document.getElementById('bookingDetailsModal').style.display = 'block';
    fetchBookingDetails(bookingID);
}

// Close Booking Details Modal
function closeBookingDetailsModal() {
    const sections = {
        flights: { table: 'details-flights-table', message: 'no-flights-message' },
        hotels: { table: 'details-hotels-table', message: 'no-hotels-message' },
        cars: { table: 'details-cars-table', message: 'no-cars-message' },
    };

    // Clear and hide all sections
    for (const key in sections) {
        const table = document.getElementById(sections[key].table);
        const tableBody = table.querySelector('tbody');
        const message = document.getElementById(sections[key].message);

        tableBody.innerHTML = ''; // Clear table content
        table.style.display = 'none'; // Hide table
        message.style.display = 'none'; // Hide "No data" message
    }

    // Hide the modal
    document.getElementById('bookingDetailsModal').style.display = 'none';
}

// Fetch Booking Details
async function fetchBookingDetails(bookingID) {
    const endpoints = {
        flights: `http://localhost:5000/api/flights/booking/${bookingID}`,
        hotels: `http://localhost:5000/api/hotels/booking/${bookingID}`,
        cars: `http://localhost:5000/api/cars/booking/${bookingID}`,
    };

    const sections = {
        flights: { table: 'details-flights-table', message: 'no-flights-message' },
        hotels: { table: 'details-hotels-table', message: 'no-hotels-message' },
        cars: { table: 'details-cars-table', message: 'no-cars-message' },
    };

    try {
        // Fetch all data in parallel
        const responses = await Promise.all(
            Object.entries(endpoints).map(([key, url]) => fetch(url).then(res => res.json()))
        );

        responses.forEach((data, index) => {
            const key = Object.keys(endpoints)[index];
            const tableBody = document.getElementById(sections[key].table).querySelector('tbody');
            const table = document.getElementById(sections[key].table);
            const message = document.getElementById(sections[key].message);

            tableBody.innerHTML = ''; // Clear old data
            table.style.display = 'none'; // Hide table by default
            message.style.display = 'none'; // Hide "No data" message

            if (data.success && data[key] && data[key].length > 0) {
                tableBody.innerHTML = data[key]
                    .map(item => {
                        if (key === 'flights') {
                            return `<tr>
                                <td>${item.id_vuelo}</td>
                                <td>${item.id_reserva}</td>
                                <td>${item.numero_billete}</td>
                                <td>${item.numero_asiento || 'N/A'}</td>
                            </tr>`;
                        } else if (key === 'hotels') {
                            return `<tr>
                                <td>${item.id_reserva}</td>
                                <td>${item.id_hotel}</td>
                                <td>${item.numero_habitacion || 'N/A'}</td>
                            </tr>`;
                        } else if (key === 'cars') {
                            return `<tr>
                                <td>${item.id_reserva}</td>
                                <td>${item.matricula_coche}</td>
                            </tr>`;
                        }
                    })
                    .join('');
                table.style.display = 'table'; // Show table
            } else {
                message.style.display = 'block'; // Show "No data" message
            }
        });
    } catch (error) {
        console.error('Error fetching booking details:', error);
        for (const key in sections) {
            const message = document.getElementById(sections[key].message);
            message.textContent = `Error loading ${key}. Please try again later.`;
            message.style.display = 'block';
        }
    }
}

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
    const closeButton = document.getElementById('close-tables-button') || createCloseButton();

    // Related sections
    const relatedSections = document.querySelectorAll('#flights-section, #hotels-section, #cars-section');

    // Clear previous booking summary and hide related sections
    tableBody.innerHTML = '';
    summaryTable.style.display = 'none';
    noBookingsMessage.style.display = 'none';
    relatedSections.forEach(section => section.style.display = 'none');
    closeButton.style.display = 'none';

    fetch(`http://localhost:5000/api/bookings/code/${bookingCode}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.booking) {
            const booking = data.booking;
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${booking.id}</td>
                <td>${booking.dni}</td>
                <td>${booking.start_date || 'N/A'}</td>
                <td>${booking.end_date || 'N/A'}</td>
            `;
            tableBody.appendChild(row);

            summaryTable.style.display = 'table';
            // Show related sections and close button if booking is found
            relatedSections.forEach(section => section.style.display = 'block');
            closeButton.style.display = 'block';
        } else {
            noBookingsMessage.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error fetching booking:', error);
        noBookingsMessage.textContent = 'Error loading booking. Please try again later.';
        noBookingsMessage.style.display = 'block';
    });

    // Fetch related details (flights, hotels, cars)
    const sections = {
        flights: {
            table: document.getElementById('flights-table'),
            message: document.getElementById('no-flights-message')
        },
        hotels: {
            table: document.getElementById('hotels-table'),
            message: document.getElementById('no-hotels-message')
        },
        cars: {
            table: document.getElementById('cars-table'),
            message: document.getElementById('no-cars-message')
        }
    };

    Object.values(sections).forEach(section => {
        section.table.querySelector('tbody').innerHTML = '';
        section.table.style.display = 'none';
        section.message.style.display = 'none';
    });

    const endpoints = {
        flights: `http://localhost:5000/api/flights/booking/${bookingCode}`,
        hotels: `http://localhost:5000/api/hotels/booking/${bookingCode}`,
        cars: `http://localhost:5000/api/cars/booking/${bookingCode}`
    };

    for (const [key, url] of Object.entries(endpoints)) {
        fetch(url, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            const section = sections[key];

            if (data.success && data[key] && data[key].length > 0) {
                const tbody = section.table.querySelector('tbody');
                tbody.innerHTML = data[key].map(item => {
                    if (key === 'flights') {
                        return `<tr>
                            <td>${item.id_vuelo}</td>
                            <td>${item.id_reserva}</td>
                            <td>${item.numero_billete}</td>
                            <td>${item.numero_asiento || 'N/A'}</td>
                        </tr>`;
                    } else if (key === 'hotels') {
                        return `<tr>
                            <td>${item.id_reserva}</td>
                            <td>${item.id_hotel}</td>
                            <td>${item.numero_habitacion || 'N/A'}</td>
                        </tr>`;
                    } else if (key === 'cars') {
                        return `<tr>
                            <td>${item.id_reserva}</td>
                            <td>${item.matricula_coche}</td>
                        </tr>`;
                    }
                }).join('');

                section.table.style.display = 'table';
            } else {
                section.message.style.display = 'block';
            }
        })
        .catch(error => {
            console.error(`Error fetching ${key}:`, error);
            sections[key].message.textContent = `Error loading ${key}. Please try again later.`;
            sections[key].message.style.display = 'block';
        });
    }
}

function createCloseButton() {
    const closeButton = document.createElement('button');
    closeButton.id = 'close-tables-button';
    closeButton.textContent = 'Close Tables';
    closeButton.style.display = 'none';
    closeButton.onclick = closeTables;
    document.getElementById('booking-summary-2').appendChild(closeButton);
    return closeButton;
}

function closeTables() {
    document.querySelectorAll('#summary-table-2, #flights-section, #hotels-section, #cars-section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById('close-tables-button').style.display = 'none';
}


function searchFlights(event) {
    event.preventDefault();

    const cityOrigin = document.getElementById('city-origin').value;
    const cityDestination = document.getElementById('city-destination').value;

    const flightsTable = document.getElementById('flights-table');
    const tableBody = flightsTable.querySelector('tbody');
    const noFlightsMessage = document.getElementById('no-flights-message-2');

    // Clear previous results
    tableBody.innerHTML = '';
    flightsTable.style.display = 'none';
    noFlightsMessage.style.display = 'none';

    // Send data via GET
    fetch(`http://localhost:5000/api/flights/route?origin=${encodeURIComponent(cityOrigin)}&destination=${encodeURIComponent(cityDestination)}`, {
        method: 'GET', // Use GET for retrieving data
        headers: { 'Content-Type': 'application/json' },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.flights) {
            data.flights.forEach(flight => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${flight.id_trayecto}</td>
                    <td>${flight.origen}</td>
                    <td>${flight.destino}</td>
                    <td>${flight.hora_salida}</td>
                    <td>${flight.hora_llegada}</td>
                    <td>
                        <button id='book-button' onclick="openBookFlightModal('${flight.id_trayecto}', '${flight.destino}')">Book</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            flightsTable.style.display = 'table';
        } else {
            noFlightsMessage.textContent = data.message || 'No flights found.';
            noFlightsMessage.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error fetching flights:', error);
        noFlightsMessage.textContent = 'Error loading flights. Please try again later.';
        noFlightsMessage.style.display = 'block';
    });
}

function openBookFlightModal(routeID, destination) {
    currentRouteID = routeID;
    currentFlightDestination = destination; // Save the destination
    console.log(`Current Destination: ${currentFlightDestination}`); // Debugging

    document.getElementById('seat-selection').style.display = 'none';
    document.getElementById('continue-button').style.display = 'inline-block';
    document.getElementById('confirm-button').style.display = 'none';
    bookFlightModal.style.display = 'block';
}


function closeBookFlightModal() {
    currentRouteID = null;
    bookFlightModal.style.display = 'none';
    document.getElementById('book-flight-form').reset();
    document.getElementById('booking-success').style.display = 'none';
    document.getElementById('booking-fail').style.display = 'none';
}

function handleContinue() {
    const departureDate = document.getElementById('departure-date').value;

    // Validate the date field
    if (!departureDate) {
        alert('Please select a departure date.');
        return;
    }

    // Hide the continue button and show the confirm booking button and seat selection
    document.getElementById('continue-button').style.display = 'none';
    document.getElementById('seat-selection').style.display = 'block';
    document.getElementById('confirm-button').style.display = 'inline-block';

    // Populate seat selection (example: fetch available seats from API)
    populateSeats(departureDate);
}

async function populateSeats(departureDate) {
    try {
        const response = await fetch(`http://localhost:5000/api/flights/check/${currentRouteID}/${departureDate}`);
        const data = await response.json();

        if (data.success && data.available_seats) {
            const seatSelect = document.getElementById('seat-number');
            seatSelect.innerHTML = ''; // Clear previous options
            data.available_seats.forEach(seat => {
                const option = document.createElement('option');
                option.value = seat;
                option.textContent = `Seat ${seat}`;
                seatSelect.appendChild(option);
            });
        } else {
            alert(data.message || 'No seats available.');
        }
    } catch (error) {
        console.error('Error fetching seats:', error);
    }
}

async function submitBooking() {
    const departureDate = document.getElementById('departure-date').value;
    const seatNumber = document.getElementById('seat-number').value;

    if (!seatNumber) {
        alert('Please select a seat.');
        return;
    }

    let createdFlightID = null;

    try {
        const response = await fetch('http://localhost:5000/api/flights/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                date: departureDate,
                id_trayecto: currentRouteID,
            }),
        });

        const data = await response.json();

        if (data.success) {
            createdFlightID = data.id_vuelo;
            document.getElementById('booking-fail').style.display = 'none';
        } else {
            document.getElementById('booking-fail').textContent = data.message || 'Flight creation failed.';
            document.getElementById('booking-fail').style.display = 'block';
            return;
        }

    } catch (error) {
        console.error('Error creating flight:', error);
        document.getElementById('booking-fail').textContent = 'An error occurred during flight creation.';
        document.getElementById('booking-fail').style.display = 'block';
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/api/booking/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                DNI: localStorage.getItem('customerDNI'),
                FECHA_INICIO: departureDate,
                FECHA_FINAL: departureDate,
                ID_VUELO: createdFlightID,
                NUMERO_ASIENTO: seatNumber,
                ID_HOTEL: selectedHotelID,
                MATRICULA_COCHE: selectedCarID,
            }),
        });

        const data = await response.json();

        if (data.success) {
            // Hide the form and show booking summary
            document.getElementById('book-flight-form').style.display = 'none';
            document.getElementById('booking-success').style.display = 'none';
        
            // Populate booking summary
            const summary = `
                <h3>Flight booked successfully!</h3>
                <p><strong>Booking ID:</strong> ${data.id_reserva}</p>
                <p><strong>Flight ID:</strong> ${data.id_vuelo}</p>
                <p><strong>Ticket Number:</strong> ${data.numero_billete}</p>
                <p><strong>Departure Date:</strong> ${data.fecha_inicio}</p>
                <p><strong>Seat Number:</strong> ${data.numero_asiento}</p>
            `;
            const summaryDetails = document.getElementById('summary-details');
            summaryDetails.innerHTML = summary;
        
            // Show the summary section
            const bookingSummary = document.getElementById('booking-summary-content');
            bookingSummary.style.display = 'block';
        } else {
            document.getElementById('booking-fail').textContent = data.message || 'Booking failed.';
            document.getElementById('booking-fail').style.display = 'block';
        }
    } catch (error) {
        console.error('Error submitting booking:', error);
        document.getElementById('booking-fail').textContent = 'An error occurred during booking.';
        document.getElementById('booking-fail').style.display = 'block';
    }

    populateBookingSummary();
}

function closeSummary() {
    const bookingSummary = document.getElementById('booking-summary-content');
    bookingSummary.style.display = 'none';
    closeBookFlightModal();
    document.getElementById('book-flight-form').style.display = 'block';    
}

function printSummary() {
    const summaryDetails = document.getElementById('summary-details').innerHTML;

    // Open a new window and print the summary
    const printWindow = window.open('', '', 'height=500,width=800');
    printWindow.document.write('<html><head><title>Booking Summary</title></head><body>');
    printWindow.document.write('<h2>Booking Summary</h2>');
    printWindow.document.write(summaryDetails);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    // printWindow.print();
}

async function fetchAvailableHotels() {
    try {
        const destination = currentFlightDestination; // Set destination dynamically
        const response = await fetch(`http://localhost:5000/api/hotels/${destination}`);
        const data = await response.json();

        if (data.success) {
            const tableBody = document.getElementById('hotel-table').querySelector('tbody');
            tableBody.innerHTML = ''; // Clear previous data
            data.hotels.forEach(hotel => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${hotel.name}</td>
                    <td>${hotel.city}</td>
                    <td>${hotel.price}€</td>
                    <td><button onclick="selectHotel('${hotel.id}', '${hotel.name}', '${hotel.city}', '${hotel.price}')">Select</button></td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error fetching hotels:', error);
    }
}

async function fetchAvailableCars() {
    try {
        const destination = currentFlightDestination; // Set destination dynamically
        const response = await fetch(`http://localhost:5000/api/cars/${destination}`);
        const data = await response.json();

        if (data.success) {
            const tableBody = document.getElementById('car-table').querySelector('tbody');
            tableBody.innerHTML = ''; // Clear previous data
            data.cars.forEach(car => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${car.model}</td>
                    <td>${car.location}</td>
                    <td>${car.price}€</td>   
                    <td><button onclick="selectCar('${car.id}', '${car.model}', '${car.location}', '${car.price}')">Select</button></td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error fetching cars:', error);
    }
}

function selectHotel(hotelID, hotelName, city, price) {
    const hotelTable = document.getElementById('hotel-table');
    const hotelHeader = document.getElementById('hotel-table-header');

    // Update header only if not already selected
    if (hotelHeader.textContent !== 'Selected Hotel') {
        hotelHeader.textContent = 'Selected Hotel';
    }

    // Clear table and display selected hotel
    hotelTable.querySelector('tbody').innerHTML = `
        <tr>
            <td>${hotelName}</td>
            <td>${city}</td>
            <td>${price}€</td>
            <td><button style='background-color: var(--error-red);' onclick="cancelHotel()">Cancel</button></td>
        </tr>
    `;

    // Store the selected hotel ID
    selectedHotelID = hotelID;
}

function toggleHotelTable() {
    const addHotel = document.getElementById('add-hotel').checked;
    const hotelTableContainer = document.getElementById('hotel-table-container');

    if (addHotel) {
        hotelTableContainer.style.display = 'block';
        fetchAvailableHotels(); // Ensure this does not reset the header or table
    } else {
        hotelTableContainer.style.display = 'none';
    }
}

function cancelHotel(hotelID) {
    const hotelTable = document.getElementById('hotel-table');
    const hotelHeader = document.getElementById('hotel-table-header');

    // Reset header
    hotelHeader.textContent = 'Available Hotels';

    toggleHotelTable(); // Reload available hotels
    selectedHotelID = null;
}

function selectCar(carID, carModel, city, price) {
    const carTable = document.getElementById('car-table');
    const carHeader = document.getElementById('car-table-header');

    // Update header only if not already selected
    if (carHeader.textContent !== 'Selected Car') {
        carHeader.textContent = 'Selected Car';
    }

    // Clear table and display selected hotel
    carTable.querySelector('tbody').innerHTML = `
        <tr>
            <td>${carModel}</td>
            <td>${city}</td>
            <td>${price}€</td>
            <td><button style='background-color: var(--error-red);' onclick="cancelCar()">Cancel</button></td>
        </tr>
    `;
    selectedCarID = carID;
}

function toggleCarTable() {
    const addCar = document.getElementById('add-car').checked;
    const carTableContainer = document.getElementById('car-table-container');

    if (addCar) {
        carTableContainer.style.display = 'block';
        fetchAvailableCars(); // Ensure this does not reset the header or table
    } else {
        carTableContainer.style.display = 'none';
    }
}

function cancelCar(carID) {
    const carTable = document.getElementById('hotel-table');
    const carHeader = document.getElementById('car-table-header');

    // Reset header
    carHeader.textContent = 'Available Cars';

    toggleCarTable(); // Reload available cars

    selectedCarID = null;
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
    // alert('Agent portal is under development.');
    localStorage.setItem('customerDNI', '00000000A');
    localStorage.setItem('customerName', 'Agent');

    // document.getElementById('registrationSuccess').style.display = 'block';

    setTimeout(() => {
        // closeClientModal();
        // Store login state (in a real app, you'd use proper authentication)
        localStorage.setItem('isLoggedIn', 'true');
        // Redirect to client portal
        window.location.href = 'static/agent-portal.html';
    }, 1000);
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



