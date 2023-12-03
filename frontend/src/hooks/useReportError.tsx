import { useEffect } from "react";
import { Notification, Typography } from "@douyinfe/semi-ui";

export function useReportGlobalError() {
  useEffect(() => {
    const handleError = (e: WindowEventMap["error"]) => {
      showError(e.message);
    };
    const handleRejection = (e: WindowEventMap["unhandledrejection"]) => {
      showError(e.reason);
    };
    window.addEventListener("error", handleError);
    window.addEventListener("unhandledrejection", handleRejection);
    return () => {
      window.removeEventListener("error", handleError);
      window.removeEventListener("unhandledrejection", handleRejection);
    };
  }, []);
}

function showError(errorText: string) {
  Notification.error({
    content: (
      <div>
        <Typography.Text>Frontend App Error</Typography.Text>
        <div
          style={{
            fontFamily: "monospace",
            whiteSpace: "pre-wrap",
            maxWidth: "400px",
            maxHeight: "200px",
            overflow: "auto",
          }}
        >
          {errorText}
        </div>
      </div>
    ),
    duration: 10,
  });
}
