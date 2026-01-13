export async function addWatchlistItem(url: string) {
  await fetch("http://localhost:8000/watchlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
}
