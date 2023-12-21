export type SingleOrRange<T> = T | [T, T];

export interface Condition {
  id?: SingleOrRange<number>;
  timestamp?: SingleOrRange<string>;
  series?: string;
  order?: Record<string, "ASC" | "DESC">;
  limit?: number;
  runId?: string;
  runId?: string;
}

export function createCondition(condition: Condition) {
  if (condition.runId) {
    condition.runId = condition.runId;
    delete condition.runId;
  }
  return new URLSearchParams({ condition: JSON.stringify({ ...condition }) }).toString();
}
