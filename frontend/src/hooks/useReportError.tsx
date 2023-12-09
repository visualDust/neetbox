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

let errorCount = 0;

function showError(errorText: string) {
  errorCount++;
  addNotice({
    id: "app-error",
    type: "error",
    title: `Frontend App Error (${errorCount})`,
    content: (
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
    ),
    duration: 10,
  });
}
