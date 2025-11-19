"use client";

import PacketRow from "./PacketRow";

export default function PacketTable({ packets }: { packets: any[] }) {
  if (packets.length === 0) {
    return <p className="text-center text-gray-500 mt-10">No packets found.</p>;
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl shadow-lg overflow-y-auto max-h-[75vh]">
      {/* Header */}
      <div className="grid grid-cols-5 gap-4 px-6 py-3 border-b border-gray-800 text-gray-300 text-sm font-semibold sticky top-0 bg-gray-900/95 backdrop-blur z-10">
        <p>Source IP</p>
        <p>Destination IP</p>
        <p>Protocol</p>
        <p>Timestamp</p>
        <p>Report Snippet</p>
      </div>

      {/* Rows */}
      <div className="p-2 space-y-2">
        {packets.map((packet, idx) => (
          <PacketRow key={packet._id} packet={packet} index={idx} />
        ))}
      </div>
    </div>
  );
}
