import http from 'http';
import fs from 'fs/promises';

import { saveToDatabase } from './database.js';

const PORT = 4000;

const server = http.createServer(async (req, res) => {
    if (req.method === 'POST' && req.url === '/receive') {
        let body = '';

        req.on('data', (chunk) => {
            body += chunk;
        });

        req.on('end', async () => {
            try {
                const request = JSON.parse(body);

                await fs.writeFile('./temporary.json', JSON.stringify(request, null, 4));

                await saveToDatabase(request);

                res.writeHead(200, {
                    'Content-Type': 'application/json; charset=utf-8',
                });

                res.end(
                    JSON.stringify({
                        message: 'Данные получены и сохранены',
                    }),
                );
            } catch (error) {
                console.error(error);

                res.writeHead(500, {
                    'Content-Type': 'application/json; charset=utf-8',
                });

                res.end(
                    JSON.stringify({
                        message: 'Ошибка сохранения',
                    }),
                );
            }
        });

        return;
    }

    res.writeHead(404);
    res.end('Not Found');
});

server.listen(PORT, () => {
    console.log(`DATABASE запущена на порту ${PORT}`);
});
