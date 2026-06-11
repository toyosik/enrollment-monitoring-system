const express = require('express');
const app = express();
const PORT = 3000;

app.use(express.json());

// Track open client connections for real-time streaming
let clients = [];

// SSE (Server-Sent Events) Endpoint for frontend dashboards
app.get('/events', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders();

    clients.push(res);

    req.on('close', () => {
        clients = clients.filter(client => client !== res);
    });
});

// Endpoint for the Python pipeline to drop alert payloads
app.post('/api/alert', (express.json()), (req, res) => {
    const alertData = req.body;
    
    console.log(`[ALERT] Real-time seat opening detected: ${alertData.course_id}`);

    // Broadcast the alert message instantly to all connected UI clients
    clients.forEach(client => {
        client.write(`data: ${JSON.stringify(alertData)}\n\n`);
    });

    res.status(200).json({ status: 'Broadcasted' });
});

app.listen(PORT, () => {
    console.log(`[Node.js Server] Real-time engine listening on port ${PORT}`);
    console.log(`[Node.js Server] Clients can stream active notifications at http://localhost:${PORT}/events`);
});
