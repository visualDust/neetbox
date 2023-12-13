export class TimeDataMapper<TTarget = any, TSource extends { timestamp: string } = any> {
  constructor(
    readonly data: Array<TSource>,
    readonly mapper: (value: TSource) => TTarget,
  ) {}

  get length() {
    return this.data.length;
  }

  chain<TNewTarget>(chainMapper: (value: TTarget) => TNewTarget) {
    return new TimeDataMapper(this.data, (x) => chainMapper(this.mapper(x)));
  }

  map<T>(fn: (timestamp: string, value: TTarget) => T) {
    return this.data.map((x) => fn(x.timestamp, this.mapper(x)));
  }

  mapTimestamp<T>(fn: (timestamp: string) => T) {
    return this.data.map((x) => fn(x.timestamp));
  }

  mapValue<T>(fn: (value: TTarget) => T) {
    return this.data.map((x) => fn(this.mapper(x)));
  }

  getValue(index: number) {
    return this.mapper(this.data[index]);
  }
}
