import { addNotice } from "../utils/notification";
import { Project } from "./projects";
import { LogData } from "./types";

const NotificationSeries = ["mention", "error"];

let lastNotification: Notification | null = null;

export function checkLogForNotification(log: LogData, project: Project) {
  if (NotificationSeries.includes(log.series)) {
    const title = `${log.series} from ${project.nameOrId}`;
    const body = `${log.whom}: ${log.message}`;
    addNotice({
      id: "log-mentions",
      type: log.series == "mention" ? "info" : "error",
      title,
      content: body,
      duration: 0,
    });
    if (!lastNotification) {
      lastNotification = new Notification(title, {
        body,
      });
      lastNotification.onclose = () => {
        lastNotification = null;
      };
    }
  }
}

Notification.requestPermission().then(() => {
  console.info("notification permission granted");
});
