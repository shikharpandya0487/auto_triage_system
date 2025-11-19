"use client";

import InfoBox from "./InfoBox";

export default function PacketInfoGrid({ msg }: { msg: any }) {
  return (
    <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
      <InfoBox label="Source MAC" value={msg["iana:sourceMacAddress"]} />
      <InfoBox label="Destination MAC" value={msg["iana:destinationMacAddress"]} />
      <InfoBox label="Source IP" value={msg["iana:sourceIPv4Address"]} />
      <InfoBox label="Destination IP" value={msg["iana:destinationIPv4Address"]} />
      <InfoBox label="Protocol" value={msg["iana:protocolIdentifier"]} />
      <InfoBox label="Flow Start" value={msg["iana:flowStartMilliseconds"]} />
      <InfoBox label="Flow End" value={msg["iana:flowEndMilliseconds"]} />
    </div>
  );
}
