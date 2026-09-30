const DATABASE_URL = 'http://database:4000/receive';

export async function transferData(request) {
    const response = await fetch(DATABASE_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
    });

    if (!response.ok) {
        throw new Error('Не удалось передать данные в DATABASE');
    }

    console.log('Данные переданы в DATABASE');
}