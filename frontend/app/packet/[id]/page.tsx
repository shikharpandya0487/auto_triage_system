
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import PacketInfoGrid from "@/components/PacketInfoGrid";
import CollapsibleSection from "@/components/CollapsibleSection";
import ChatButton from "@/components/ChatButton";
import ChatPanel from "@/components/ChatPanel";

export default function PacketDetailsPage() {
  const { id } = useParams();
  const [packet, setPacket] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    if (!id) return;

    const fetchPacket = async () => {
      try {
        const res = await fetch(`/api/packetDetails/${id}`, { cache: "no-store" });
        if (!res.ok) throw new Error(`Failed to fetch packet: ${res.statusText}`);
        const data = await res.json();
        setPacket(data);
      } catch (err: any) {
        console.error("Error fetching packet:", err);
        setError(err.message);
      }
    };

    fetchPacket();
  }, [id]);

  if (error)
    return (
      <div className="p-8 text-red-400 text-center bg-gray-950 min-h-screen flex items-center justify-center">
        ⚠️ {error}
      </div>
    );

  if (!packet)
    return (
      <div className="p-8 text-gray-400 text-center bg-gray-950 min-h-screen flex items-center justify-center">
        Loading packet details...
      </div>
    );

  const msg = packet.packet || {};

  return (
    <main className="relative min-h-screen bg-gray-950 text-gray-100 flex">
      {/* Left side: Packet Details */}
      <div
        className={`transition-all duration-300 overflow-y-auto p-8 ${
          showChat ? "w-1/2" : "w-full"
        }`}
      >
        <h1 className="text-3xl font-bold mb-6 border-b border-gray-700 pb-2">
          Packet Details
        </h1>

        <PacketInfoGrid msg={msg} />

        <CollapsibleSection
          title="Agent Report"
          markdown
          content={ Array.isArray(packet.threat_report)
    ? packet.threat_report[0]?.text || "No report data"
    : packet.threat_report || "No report data"}
        />

        <CollapsibleSection
          title="Full Message Object"
          content={msg}
        />
        {!showChat && (
        <div className="mt-6">
          <ChatButton onClick={() => setShowChat(true)} />
        </div>
      
      )}
      </div>

      {/* Right side: Chat Panel */}
      {showChat && <ChatPanel packet={msg} onClose={() => setShowChat(false)} />}
    </main>
  );
}
