import { Spin } from "@douyinfe/semi-ui";
import { SpinSize } from "@douyinfe/semi-ui/lib/es/spin";

export default function Loading({
  width = "",
  height = "100px",
  size = "middle",
}: {
  width?: string;
  height?: string;
  size?: SpinSize;
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
      <Spin size={size} />
    </div>
  );
}
