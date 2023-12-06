import { Notification } from "@douyinfe/semi-ui";

Notification.config({
  top: "60px",
  right: "10px",
});

export const addNotice = Notification.addNotice.bind(Notification);
