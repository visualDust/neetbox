import useSWR from "swr";

export const API_BASEURL = "/web";
export const WEBSOCKET_URL = import.meta.env.DEV
  ? "ws://localhost:5001"
  : `ws://${location.hostname}:${Number(location.port) + 1}`;

async function fetcher(url: string) {
  const res = await fetch(API_BASEURL + url);
  return await res.json();
}

export function useAPI(url: string, options?: { refreshInterval?: number }) {
  return useSWR(url, fetcher, options);
}
