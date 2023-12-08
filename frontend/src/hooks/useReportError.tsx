import { useEffect } from "react";
import { Typography } from "@douyinfe/semi-ui";
import { addNotice } from "../utils/notification";

export function useReportGlobalError() {
  useEffect(() => {
    const handleError = (e: WindowEventMap["error"]) => {
      showError(e.message);
    };
    const handleRejection = (e: WindowEventMap["unhandledrejection"]) => {
      showError(String(e.reason));
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
  addNotice({
    type: "error",
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
