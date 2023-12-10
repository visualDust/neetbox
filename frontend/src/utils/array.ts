export function slideWindow<T>(arr: T[], items: T[], max: number) {
  arr = arr.slice(arr.length + items.length > max ? arr.length + items.length - max : 0);
  arr.push(...items);
  return arr;
}
