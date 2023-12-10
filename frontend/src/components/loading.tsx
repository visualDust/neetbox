import { Space, Spin } from "@douyinfe/semi-ui";
import { SpinSize } from "@douyinfe/semi-ui/lib/es/spin";
import { ReactNode } from "react";

export default function Loading({
  width = "",
  height = "100px",
  size = "middle",
  text,
}: {
  width?: string;
  height?: string;
  size?: SpinSize;
  text?: ReactNode;
}) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width,
        height,
      }}
    >
      {text ? (
        <Space>
          <Spin size={size} />
          {text}
        </Space>
      ) : (
        <Spin size={size} />
      )}
    </div>
  );
}
