import clientPromise from "@/lib/mongodb";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const client = await clientPromise;
    const db = client.db("test");
    const packets = await db.collection("ipfix").find().sort({ timestamp: -1 }).limit(50).toArray();

    return NextResponse.json(packets);
  } catch (err) {
    console.error("Error fetching packets:", err);
    return NextResponse.json({ error: "Failed to fetch packets" }, { status: 500 });
  }
}
