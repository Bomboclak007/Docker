import { createClient } from 'redis';

const client = createClient({
    socket: {
        host: 'redis',
        port: 6379,
    },
});

client.on('error', (err) => {
    console.error('Redis error:', err);
});

client.on('connect', () => {
    console.log('Подключились к Redis');
});

await client.connect();

export default client;