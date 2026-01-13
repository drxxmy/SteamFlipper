export async function addWatchlistItem(url: string) {
  const res = await fetch("http://localhost:8000/watchlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) throw new Error("Failed to add item");
  return res.json();
}
