export function slideWindow<T>(arr: T[], newItems: T[], count: number | undefined, sliceThreshold = count) {
  if (count && sliceThreshold && arr.length + newItems.length > sliceThreshold) {
    arr = arr.slice(arr.length + newItems.length > sliceThreshold ? arr.length + newItems.length - count : 0);
    arr.push(...newItems);
  } else {
    return [...arr, ...newItems];
  }
  return arr;
}
