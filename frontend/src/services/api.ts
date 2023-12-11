import useSWR from "swr";

export const API_BASEURL = "/api";
export const WEBSOCKET_URL =
  process.env.NODE_ENV === "development"
    ? `ws://${location.host}/ws/`
    : `ws://${location.hostname}:${Number(location.port) + 1}`;

export async function fetcher(url: string, fetchInit?: RequestInit) {
  const res = await fetch(API_BASEURL + url, fetchInit);
  try {
    if (!res.ok) new Error(`HTTP status ${res.status}: ${res.body}`);
    return await res.json();
  } catch (e) {
    throw new Error(`fetching ${url}: ${e}`);
  }
}

export function useAPI(url: string | null, options?: { refreshInterval?: number; fetcher?: typeof fetcher }) {
  return useSWR(url, options?.fetcher ?? fetcher, { keepPreviousData: false, ...options });
}
