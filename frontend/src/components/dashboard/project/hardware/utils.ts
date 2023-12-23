import { TimeDataMapper } from "../../../../utils/timeDataMapper";

const viewRangeSeconds = 300;
const dataInterval = 2;
export const fetchDataCount = Math.ceil((viewRangeSeconds / dataInterval) * 1.1);

export function getTimeAxisOptions(mapper: TimeDataMapper) {
  const latestTime = new Date(mapper.data[mapper.data.length - 1].timestamp).getTime();
  return {
    min: latestTime - viewRangeSeconds * 1000,
    max: latestTime,
  };
}

export function green2redHue(value) {
  return ((1 - value) * 120).toString(10);
}
