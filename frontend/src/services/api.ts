import useSWR from "swr";

export const API_BASEURL = "/web";
export const WEBSOCKET_URL = import.meta.env.DEV || (process.env.NODE_ENV === 'development')
  ? `ws://${location.host}/ws/`
  : `ws://${location.hostname}:${Number(location.port) + 1}`;

export async function fetcher(url: string) {
  const res = await fetch(API_BASEURL + url);
  return await res.json();
}

export function useAPI(url: string | null, options?: { refreshInterval?: number }) {
  return useSWR(url, fetcher, options);
}
