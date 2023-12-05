import { useMemo } from "react";

/** Return the same ref if the data is not changed */
export function useMemoJSON<T>(data: T): T {
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useMemo(() => data, [JSON.stringify(data)]);
}
