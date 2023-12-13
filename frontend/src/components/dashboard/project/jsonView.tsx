import JsonView from "@uiw/react-json-view";
// eslint-disable-next-line import/no-unresolved
import { darkTheme } from "@uiw/react-json-view/dark";
import { memo } from "react";
import { useTheme } from "../../../hooks/useTheme";

export const JsonViewThemed = memo((props: any) => {
  const { darkMode } = useTheme();
  return (
    <JsonView
      {...props}
      style={{ ...props?.style, ...(darkMode ? darkTheme : null), background: "transparent" }}
    />
  );
});
