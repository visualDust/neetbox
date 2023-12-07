import { Space } from "@douyinfe/semi-ui";
import { memo } from "react";
import { AllImageViewers } from "./images";
import { AllScatterViewers } from "./scatters";

export const ImagesAndScatters = memo(() => {
  return (
    <Space style={{ marginBottom: "20px" }} wrap>
      <AllImageViewers />
      <AllScatterViewers />
    </Space>
  );
});
