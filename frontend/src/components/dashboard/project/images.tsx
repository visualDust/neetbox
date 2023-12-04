import { memo } from "react";
import { Popover, Space } from "@douyinfe/semi-ui";
import { useCurrentProject, useProjectImages } from "../../../hooks/useProject";

export const Images = memo(() => {
  const { projectId } = useCurrentProject()!;
  const images = useProjectImages(projectId);
  return (
    <Space style={{ overflow: "auto", width: "100%" }}>
      {images.map((img) => (
        <Popover showArrow content={<pre>{JSON.stringify(img.metadata, null, 2)}</pre>}>
          <img src={"/web/image/" + projectId + "/" + img.imageId} />
        </Popover>
      ))}
    </Space>
  );
});
