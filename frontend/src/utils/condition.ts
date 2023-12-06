export type SingleOrRange<T> = T | [T, T];

export interface Condition {
  id?: SingleOrRange<number>;
  timestamp?: SingleOrRange<string>;
  series?: string;
  order?: Record<string, "ASC" | "DESC">;
  limit?: number;
}

export function createCondition(condition: Condition) {
  return new URLSearchParams({ condition: JSON.stringify(condition) }).toString();
}
