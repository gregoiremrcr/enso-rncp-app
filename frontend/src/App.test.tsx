import { afterAll, afterEach, beforeAll, expect, test } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import App from "./App";

const observedParams: string[] = [];
// Réponses MSW de fixture locale ; ces valeurs ne sont pas des observations NOAA.
const server = setupServer(
  http.get("http://localhost/api/v1/observations", ({ request }) => {
    const url = new URL(request.url);
    observedParams.push(
      `${url.searchParams.get("start") ?? ""}|${url.searchParams.get("end") ?? ""}`,
    );
    const value = url.searchParams.has("start") ? 1.25 : -0.75;
    return HttpResponse.json({
      index: "RONI",
      unit: "°C",
      count: 1,
      period_start: "2000-01-01",
      period_end: "2000-01-01",
      observations: [
        {
          year: 2000,
          season: "DJF",
          center_date: "2000-01-01",
          value_celsius: value,
        },
      ],
    });
  }),
  http.get("http://localhost/api/v1/source", () =>
    HttpResponse.json({
      index: "RONI",
      url: "https://example.test/roni",
      version: "fixture",
      extracted_at: "2026-11-11",
      period_start: "2000-01-01",
      period_end: "2000-01-01",
      file_sha256: "fixture",
    }),
  ),
  http.get("http://localhost/api/v1/episodes", () => HttpResponse.json([])),
);
beforeAll(() => {
  server.listen();
  const interceptedFetch = globalThis.fetch.bind(globalThis);
  globalThis.fetch = (input, init) => {
    const requestUrl =
      typeof input === "string"
        ? input
        : input instanceof URL
          ? input.href
          : input.url;
    return interceptedFetch(new URL(requestUrl, "http://localhost"), init);
  };
});
afterEach(() => {
  cleanup();
  server.resetHandlers();
  observedParams.length = 0;
});
afterAll(() => server.close());

test("appliquer une période recharge les observations et actualise la valeur affichée", async () => {
  // Le bouton évite les appels pendant la saisie incomplète d'une date.
  const user = userEvent.setup();
  render(<App />);
  expect(await screen.findByText("-0.75")).toBeInTheDocument();
  await user.type(screen.getByLabelText("Du"), "2000-01-01");
  expect(observedParams).toEqual(["|"]);
  await user.click(screen.getByRole("button", { name: "Appliquer le filtre" }));
  expect(await screen.findByText("1.25")).toBeInTheDocument();
  await waitFor(() => expect(observedParams).toContain("2000-01-01|"));
});

test("affiche la date d'extraction au format français", async () => {
  render(<App />);
  expect(
    await screen.findByText(/extraction : 11\/11\/2026/),
  ).toBeInTheDocument();
});

test("utilise le repli si l'API omet la date d'extraction", async () => {
  server.use(
    http.get("http://localhost/api/v1/source", () =>
      HttpResponse.json({
        index: "RONI",
        url: "https://example.test/roni",
        version: "fixture",
        period_start: "2000-01-01",
        period_end: "2000-01-01",
        file_sha256: "fixture",
      }),
    ),
  );
  render(<App />);
  expect(
    await screen.findByText(/extraction : date non indiquée/),
  ).toBeInTheDocument();
});
