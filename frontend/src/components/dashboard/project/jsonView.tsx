import JsonView from "@uiw/react-json-view";
// eslint-disable-next-line import/no-unresolved
import { githubDarkTheme } from "@uiw/react-json-view/githubDark";
import { CSSProperties, memo } from "react";
import { Popover, Space, Typography } from "@douyinfe/semi-ui";
import { IconCode, IconCodeStroked } from "@douyinfe/semi-icons";
import { Position } from "@douyinfe/semi-ui/lib/es/tooltip";
import { useTheme } from "../../../hooks/useTheme";
import "./jsonView.css";

export const JsonViewThemed = memo((props: any) => {
  const { darkMode } = useTheme();
  return (
    <JsonView
      displayDataTypes={false}
      {...props}
      style={{
        minWidth: 200,
        width: 400,
        maxHeight: "60vh",
        overflow: "auto",
        ...props?.style,
        ...(darkMode ? githubDarkTheme : null),
        background: "transparent",
      }}
    />
  );
});

export const JsonPopover = memo(
  ({
    value,
    title,
    position,
    style,
  }: {
    value: any;
    title?: string;
    position?: Position;
    style?: CSSProperties;
  }) => {
    return (
      <Popover
        showArrow
        position={position}
        content={
          <Space vertical>
            {title && <Typography.Text>{title}</Typography.Text>}
            <JsonViewThemed value={value} />
          </Space>
        }
      >
        <IconCodeStroked style={{ color: "var(--semi-color-tertiary)", ...style }} />
      </Popover>
    );
  },
);
