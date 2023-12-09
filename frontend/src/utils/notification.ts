import { Notification } from "@douyinfe/semi-ui";

type NoticeProps = Parameters<typeof Notification.addNotice>[0];

const defaultConfig = {
  top: "60px",
  right: "10px",
} as any;

Notification.config(defaultConfig);

export const addNotice = (notice: NoticeProps) => Notification.addNotice({ ...defaultConfig, ...notice });
