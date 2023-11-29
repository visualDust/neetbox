import { Spin } from "@douyinfe/semi-ui";

export default function Loading({ width = "", height = "100px" }: { width?: string; height?: string }) {
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
      <Spin size="large" />
    </div>
  );
}
