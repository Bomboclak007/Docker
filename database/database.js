import pg from 'pg';

const { Pool } = pg;

const pool = new Pool({
    host: 'postgres',
    port: 5432,
    database: 'requests',
    user: 'postgres',
    password: 'postgres',
});

export async function saveToDatabase(data) {
    await pool.query(
        `
        INSERT INTO requests
        (
            full_name,
            phone,
            email,
            message
        )
        VALUES ($1, $2, $3, $4)
        `,
        [data.fullName, data.phone, data.email, data.message],
    );
}