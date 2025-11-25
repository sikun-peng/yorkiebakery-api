export const HOME_URL =
  window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "";  // production → relative → same domain

export default function YorkieHeader() {
  return (
    <header className="mb-8">
      <div className="flex items-center justify-between">
        <a
          href={HOME_URL}
          className="text-2xl font-bold text-[var(--yorkie-brown)] hover:underline"
        >
          Yorkie Bakery 🐾🍪
        </a>
      </div>
    </header>
  );
}