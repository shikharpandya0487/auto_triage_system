import { NextResponse } from "next/server";
import { MongoClient, ObjectId } from "mongodb";

const uri = process.env.MONGODB_URI!;
const dbName = process.env.MONGODB_DB || "test"; 
let client: MongoClient | null = null;

async function getClient() {
  if (!client) {
    client = new MongoClient(uri);
    await client.connect();
  }
  return client;
}

export async function GET(
  req: Request,
  context: { params: Promise<{ id: string }> } 
) {
  try {
    const { id } = await context.params; 

    const client = await getClient();
    const db = client.db(dbName);
    const collection = db.collection("ipfix"); 

    const packet = await collection.findOne({ _id: new ObjectId(id) });

    if (!packet) {
      return NextResponse.json({ error: "Packet not found" }, { status: 404 });
    }

    return NextResponse.json(packet);
  } catch (error: any) {
    console.error("Error fetching packet details:", error);
    return NextResponse.json(
      { error: "Internal Server Error", details: error.message },
      { status: 500 }
    );
  }
}
