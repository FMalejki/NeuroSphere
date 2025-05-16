import { NextResponse } from 'next/server';
import connectDB from '@/config/db'; // lub ścieżka do Twojej funkcji łączenia z Mongo
import User from '@/models/User'; // upewnij się, że ścieżka jest poprawna

export async function POST(req) {
  try {
    const body = await req.json();
    const { user_id, product_id, product_name } = body;

    await connectDB();

    // Aktualizacja użytkownika: dodanie promptu
    await User.findByIdAndUpdate(
      { _id: user_id },
      {
        $push: {
          ownedProducts: {
            id: product_id,
            title: product_name,
          },
        },
      },
      { upsert: true } // stworzy użytkownika, jeśli nie istnieje
    );

    console.log(`Prompt ${product_id} added to user ${user_id}`);

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error('Error in /api/user/add-product:', err);
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
