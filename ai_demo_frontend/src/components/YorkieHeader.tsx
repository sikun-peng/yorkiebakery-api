export const HOME_URL =
  window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "/";

export default function YorkieHeader() {
  return (
    <header className="mb-6">
      <div className="flex items-center justify-between">
        <a
          href={HOME_URL}
          className="text-3xl font-bold text-[var(--yorkie-brown)] tracking-wide"
        >
          Yorkie Bakery 🐾🍪
        </a>
      </div>
    </header>
  );
}
