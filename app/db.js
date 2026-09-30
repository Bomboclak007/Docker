import pg from 'pg';
import redis from './redis.js';

const { Pool } = pg;

const pool = new Pool({
    host: 'postgres',
    port: 5432,
    database: 'requests',
    user: 'postgres',
    password: 'postgres',
});

const CACHE_TTL_SECONDS = 60 * 60; 

export async function getIdRange() {
    const { rows } = await pool.query(
        'SELECT MIN(id) AS min_id, MAX(id) AS max_id, COUNT(*) AS total FROM requests',
    );

    return rows[0];
}

export async function getRequestById(id) {
    const cacheKey = `request:${id}`;

    try {
        const cached = await redis.get(cacheKey);

        if (cached) {
            console.log(`[cache hit] id=${id}`);
            return JSON.parse(cached);
        }
    } catch (err) {
        console.error('Redis GET error:', err);
    }

    const { rows } = await pool.query(
        'SELECT id, full_name, phone, email, message, created_at FROM requests WHERE id = $1',
        [id],
    );

    const item = rows[0] || null;

    if (item) {
        try {
            await redis.set(cacheKey, JSON.stringify(item), {
                EX: CACHE_TTL_SECONDS,
            });
            console.log(`[cache miss → saved] id=${id}`);
        } catch (err) {
            console.error('Redis SET error:', err);
        }
    }

    return item;
}

export async function invalidateRequestCache(id) {
    try {
        await redis.del(`request:${id}`);
    } catch (err) {
        console.error('Redis DEL error:', err);
    }
}