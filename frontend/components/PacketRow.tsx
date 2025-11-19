"use client";

import Link from "next/link";

export default function PacketRow({ packet, index }: { packet: any; index: number }) {
  const msg = packet.packet || {};
  const report = Array.isArray(packet.threat_report)
    ? packet.threat_report[0]?.text || "No report data"
    : packet.threat_report || "No report data";

  const bgColor =
    index % 2 === 0 ? "#1b2431" : "#111827"; // zebra-strip effect (custom tone)
  
  const timestamp = packet.timestamp || "N/A"

  return (
    <Link
      href={`/packet/${packet._id}`}
      style={{ backgroundColor: bgColor }}
      className={`
        grid grid-cols-5 gap-4 px-6 py-4 rounded-xl
        
        border border-gray-800 hover:border-blue-500 hover:bg-gray-800/60
        transition-all duration-200 ease-in-out
        hover:shadow-md hover:shadow-blue-900/30
      `}
    >
      <p className="truncate">{msg["iana:sourceIPv4Address"] || "N/A"}</p>
      <p className="truncate">{msg["iana:destinationIPv4Address"] || "N/A"}</p>
      <p className="truncate">{msg["iana:protocolIdentifier"] || "N/A"}</p>
      <p className="text-gray-400 text-sm truncate">
        {timestamp!='N/A' ? new Date(timestamp).toLocaleString() : 'N/A'}
      </p>
      <p className="text-gray-500 text-sm line-clamp-1">
        {report.length > 100 ? report.slice(0, 100) + "..." : report}
      </p>
    </Link>
  );
}
