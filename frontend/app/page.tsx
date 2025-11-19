"use client";

import { useEffect, useState } from "react";
import PacketTable from "@/components/PacketTable";
import LoadingOrError from "@/components/LoadingOrError";

export default function PacketList() {
  const [packets, setPackets] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPackets = async () => {
      try {
        const res = await fetch("/api/packets", { cache: "no-store" });
        if (!res.ok) throw new Error(`Failed: ${res.statusText}`);
        const data = await res.json();
        setPackets(data);
      } catch (err: any) {
        console.error("Error fetching packets:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPackets();
  }, []);

  if (loading || error) return <LoadingOrError loading={loading} error={error} />;

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 p-10">
      <h1 className="text-3xl font-bold mb-8 border-b border-gray-800 pb-3 text-center">
        🌐 Network Packets
      </h1>
      <PacketTable packets={packets} />
    </main>
  );
}
