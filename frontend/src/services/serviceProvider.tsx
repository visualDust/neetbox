import { PropsWithChildren, useEffect } from "react";
import { startBackgroundTasks } from "./projects";

export function ServiceProvider({ children }: PropsWithChildren) {
  useEffect(() => {
    const tasks = startBackgroundTasks();
    return () => tasks.dispose();
  });
  return children;
}
