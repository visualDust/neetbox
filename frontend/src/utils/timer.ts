export class IdleTimer {
  id: number | null = null;
  get running() {
    return Boolean(this.id);
  }

  constructor(public callback: () => void) {}

  private _callbackWrapper = () => {
    this.callback();
    this.id = null;
  };

  schedule(timeout: number) {
    this.cancel();
    if (window.requestIdleCallback) {
      this.id = window.requestIdleCallback(this._callbackWrapper, { timeout });
    } else {
      this.id = setTimeout(this._callbackWrapper, timeout) as unknown as number;
    }
  }

  cancel() {
    if (!this.id) return;
    if (window.cancelIdleCallback) {
      window.cancelIdleCallback(this.id);
    } else {
      clearTimeout(this.id);
    }
    this.id = null;
  }
}
