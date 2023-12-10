import { TimeDataMapper } from "../../../../utils/timeDataMapper";

export function getTimeAxisOptions(mapper: TimeDataMapper) {
  const latestTime = new Date(mapper.data[mapper.data.length - 1].timestamp).getTime();
  return {
    min: latestTime - 120 * 1000,
    max: latestTime,
  };
}
