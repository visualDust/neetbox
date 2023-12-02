import { getDefaultStore, PrimitiveAtom, atom } from "jotai";

export class BetterAtom<T> {
  private _value: T;
  get value() {
    return this._value;
  }
  set value(val) {
    this._value = val;
    getDefaultStore().set(this.atom, val);
  }

  atom: PrimitiveAtom<T>;
  constructor(value: T) {
    this._value = value;
    this.atom = atom(value);
  }
}
