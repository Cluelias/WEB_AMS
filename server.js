const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Middleware to parse JSON bodies
app.use(express.json());

// Variable to track the clock-in/out status
let clockInOutEnabled = false;

// Serve static files (for simplicity, we are serving the frontend from the same server)
app.use(express.static('public'));

// Route to toggle the clock-in/out feature
app.post('/toggle_clock_in_out', (req, res) => {
    clockInOutEnabled = req.body.enable;
    // Emit the clock-in/out status to all connected clients (employees)
    io.emit('clock_in_out_status', { enabled: clockInOutEnabled });
    res.json({ message: 'Clock-in/out status updated' });
});

// Start the server
server.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
