import { memo } from "react";
import { Card, Popover, Space } from "@douyinfe/semi-ui";
import { useCurrentProject, useProjectImages } from "../../../hooks/useProject";
import { useAPI } from "../../../services/api";
import Loading from "../../loading";

export const Images = memo(() => {
  const { projectId } = useCurrentProject()!;
  const { data: series } = useAPI(`/series/${projectId}/image`);
  console.info("image series", series);
  const images = useProjectImages(projectId);
  return (
    <Space style={{ overflow: "auto", width: "100%" }}>
      {series?.map((s) => <SeriesViewer series={s} />) ?? <Loading />}
      {/* {images.map((img) => (
        <Popover showArrow content={<pre>{JSON.stringify(img.metadata, null, 2)}</pre>}>
          <img style={{ background: "white" }} src={"/web/image/" + projectId + "/" + img.imageId} />
        </Popover>
      ))} */}
    </Space>
  );
});

const SeriesViewer = ({ series }: { series: string }) => {
  return <Card>{series}</Card>;
};
