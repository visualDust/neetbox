import { ProjectStatus } from "../../../../services/types";

export function getTimeAxisOptions(hardwareData: Array<ProjectStatus["hardware"]>) {
  const latestTime = new Date(hardwareData[hardwareData.length - 1].timestamp).getTime();
  return {
    min: latestTime - 60 * 1000,
    max: latestTime,
  };
}
