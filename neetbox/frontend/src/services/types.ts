export interface ProjectStatusHistory {
  enablePolling: boolean;
  current?: ProjectStatus;
  history: Array<ProjectStatus>;
}

export interface ProjectStatus {
  config: WithTimestamp<ProjectConfig>;
  platform: WithTimestamp<Record<string, string | string[]>>;
  hardware: WithTimestamp<HardwareInfo>;
  __action: WithTimestamp<ActionInfo>;
}

interface ProjectConfig {
  name: string;
}

interface HardwareInfo {
  cpus: Array<{
    id: number;
    percent: number;
    freq: [current: number, min: number, max: number];
  }>;
  gpus: Array<{
    id: number;
    name: string;
    load: number;
    memoryUtil: number;
    memoryTotal: number;
    memoryFree: number;
    memoryUsed: number;
    temperature: number;
    driver: string;
  }>;
  ram: {
    total: number;
    available: number;
    used: number;
    free: number;
  };
}

type ActionInfo = Record<
  string,
  {
    args: Record<string, string>;
    blocking: boolean;
    description: string;
  }
>;

export interface WithTimestamp<T> {
  value: T;
  timestamp: number;
  interval: number;
}

export interface LogData {
  prefix: string;
  datetime: string;
  whom: string;
  msg: string;
  /** frontend only */
  _id: number;
}

export interface ImageMetadata {
  imageId: number;
  metadata: any;
}
