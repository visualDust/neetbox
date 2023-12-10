import useSWR from "swr";

export const API_BASEURL = "/web";
export const WEBSOCKET_URL =
  import.meta.env.DEV || process.env.NODE_ENV === "development"
    ? `ws://${location.host}/ws/`
    : `ws://${location.hostname}:${Number(location.port) + 1}`;

export async function fetcher(url: string) {
  const res = await fetch(API_BASEURL + url);
  try {
    return await res.json();
  } catch (e) {
    throw new Error(`fetching ${url}: ${e}`);
  }
}

export function useAPI(url: string | null, options?: { refreshInterval?: number; fetcher?: typeof fetcher }) {
  return useSWR(url, options?.fetcher ?? fetcher, { keepPreviousData: false, ...options });
}
