const ws = new WebSocket('ws://localhost:8080');

ws.onmessage = (event) => {
    if (event.data === 'reload') {
        console.log('Reloading the survey due to file change...');
        loadjs(`main.js?t=${new Date().getTime()}`)
    }
};

ws.onopen = () => {
    console.log('WebSocket connection for hot reloading established');
};