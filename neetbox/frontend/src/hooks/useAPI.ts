import { useEffect } from "react";
import useSWR, { mutate } from "swr";

const API_BASEPATH = "/api"

async function fetcher(url: string) {
    const res = await fetch(API_BASEPATH + url);
    return await res.json();
}

export function useAPI(url: string, options?: { refreshInterval?: number }) {
    useEffect(() => {
        if (options?.refreshInterval) {
            const timer = setInterval(() => {
                mutate(url);
            }, options.refreshInterval);
            return () => clearInterval(timer)
        }
    }, [url, options?.refreshInterval]);
    return useSWR(url, fetcher)
}
