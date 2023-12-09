export interface ProjectStatusHistory {
  enablePolling: boolean;
  current?: ProjectStatus;
  history: Array<ProjectStatus>;
}

export interface ProjectStatus {
  config: ProjectConfig;
  platform: WithTimestamp<Record<string, string | string[]>>;
  hardware: WithTimestamp<HardwareInfo>;
  __action: WithTimestamp<ActionInfo>;
}

interface ProjectConfig {
  name: string;
}

export interface CpuInfo {
  id: number;
  percent: number;
  freq: [current: number, min: number, max: number];
}

export interface GpuInfo {
  id: number;
  name: string;
  load: number;
  memoryUtil: number;
  memoryTotal: number;
  memoryFree: number;
  memoryUsed: number;
  temperature: number;
  driver: string;
}

export interface RamInfo {
  total: number;
  available: number;
  used: number;
  free: number;
}

export interface HardwareInfo {
  timestamp: string;
  cpus: Array<CpuInfo>;
  gpus: Array<GpuInfo>;
  ram: RamInfo;
}

export type ActionInfo = Record<
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
  series: string;
  timestamp: string;
  whom: string;
  message: string;
}

export interface ImageMetadata {
  imageId: number;
  metadata: {
    series: string;
  };
}
