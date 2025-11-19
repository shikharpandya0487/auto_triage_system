"use client";

export default function InfoBox({ label, value }: { label: string; value: any }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 shadow-sm">
      <p className="text-sm font-medium text-gray-400">{label}</p>
      <p className="text-gray-100 font-semibold wrap-break-words">
        {value || "—"}
      </p>
    </div>
  );
}
