import { Hono } from 'hono'
import { readFileSync } from 'fs';
import Mustache from 'mustache';
import chokidar from 'chokidar';
import type { ServerWebSocket } from 'bun';
const recaptchaKeys = require("./recaptchaKeys.json");

async function createResults(req: any) {
    const data = req;
    const token = data["g-recaptcha-token"];
    delete data["g-recaptcha-token"];
    let recaptcha_response = {};
    if (token) {
        const requestHeaders = {
            method: "POST",
            body: `secret=${recaptchaKeys.RECAPTCHA_SECRET_KEY}&response=${token}`, // URL-encoded body
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        };
        const recaptcha_fetch = await fetch("https://www.google.com/recaptcha/api/siteverify", requestHeaders);
        interface RecaptchaResponse {
            success: boolean;
            score?: number;
        }
        const recaptcha: RecaptchaResponse = await recaptcha_fetch.json();
        recaptcha_response = {
            g_recaptcha_score: recaptcha.success ? recaptcha.score : NaN,
        };
    } else {
        recaptcha_response = {
            g_recaptcha_score: NaN,
        };
    }
    return Object.assign(data, recaptcha_response)
};

const templateContent = readFileSync('./public/index.html', 'utf-8');

const app = new Hono()
app.get('/', (c) => {
    return c.html(Mustache.render(templateContent, { "RECAPTCHA_SITE_KEY": recaptchaKeys.RECAPTCHA_SITE_KEY }), 200)
})
app.get('/main.js', async (c) => {
    const jsContent = readFileSync('./build/main.js', 'utf-8');
    return c.text(jsContent, 200, { "Content-Type": "application/javascript" });
})
app.get('/reload.js', (c) => {
    const jsContent = readFileSync('./public/reload.js', 'utf-8');
    return c.text(jsContent, 200, { "Content-Type": "application/javascript" });
})
app.get("/load.js", (c) => {
    const jsContent = readFileSync('./node_modules/loadjs/dist/loadjs.min.js', 'utf-8');
    return c.text(jsContent, 200, { "Content-Type": "application/javascript" });
})

app.post("/submit/", async (c) => {
    const data = await c.req.json()
    return c.json(await createResults(data), 200)
})

export default app;

const clients = new Set<ServerWebSocket<unknown>>();

if (import.meta.main) {
    Bun.serve({
        fetch: app.fetch,
        port: 3000,
        development: true,
    });

    Bun.serve({
        fetch(req, server) {
            const success = server.upgrade(req);
            if (success) return undefined;
            return new Response("WebSocket server", { status: 200 })
        },
        port: 8080,
        websocket: {
            message(ws, message) { },
            open(ws) { clients.add(ws) },
            close(ws) { clients.delete(ws) },
        }
    })
    console.log(`Welcome to \x1b[1mVeles\x1b[0m!`);
    console.log(`Listening on:\n`);
    console.log(`\x1b[1;38;2;25;179;148mhttp://localhost:3000\x1b[0m`);
    console.log("\nPress Ctrl+C to stop the server...");

    const watcher = chokidar.watch('./build/main.js');
    watcher.on('change', () => {
        clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send('reload');
                console.log("main.js changed, reloading...");
            }
        });
    });
}