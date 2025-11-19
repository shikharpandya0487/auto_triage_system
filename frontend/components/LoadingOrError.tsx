"use client";

export default function LoadingOrError({
  loading,
  error,
}: {
  loading: boolean;
  error: string | null;
}) {
  if (loading) {
    return (
      <main className="min-h-screen bg-gray-950 text-gray-300 flex items-center justify-center">
        <p className="text-lg text-gray-400 animate-pulse">Loading packets...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-gray-950 text-red-400 flex items-center justify-center">
        ⚠️ Error loading packets: {error}
      </main>
    );
  }

  return null;
}
