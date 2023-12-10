export type SingleOrRange<T> = T | [T, T];

export interface Condition {
  id?: SingleOrRange<number>;
  timestamp?: SingleOrRange<string>;
  series?: string;
  order?: Record<string, "ASC" | "DESC">;
  limit?: number;
  runid?: string;
  runId?: string;
}

export function createCondition(condition: Condition) {
  if (condition.runId) {
    condition.runid = condition.runId;
    delete condition.runId;
  }
  return new URLSearchParams({ condition: JSON.stringify({ ...condition }) }).toString();
}
