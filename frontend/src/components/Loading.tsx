export function Loading({ children = "Chargement…" }: { children?: string }) {
  return <p role="status">{children}</p>;
}
