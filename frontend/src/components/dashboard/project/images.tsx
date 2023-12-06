import { memo, useEffect, useState } from "react";
import { Button, Card, Input, Popover, Space } from "@douyinfe/semi-ui";
import { useCurrentProject, useProjectImages } from "../../../hooks/useProject";
import { useAPI } from "../../../services/api";
import Loading from "../../loading";
import { createCondition } from "../../../utils/condition";

export const Images = memo(() => {
  const { projectId } = useCurrentProject()!;
  const { data: series } = useAPI(`/series/${projectId}/image`);
  console.info("image series", series);
  // const images = useProjectImages(projectId);
  console.info({ series });
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
  const { projectId } = useCurrentProject()!;
  const { data } = useAPI(
    `/image/${projectId}/history?${createCondition({
      series,
      limit: 1000,
      order: {
        id: "DESC",
      },
    })}`,
  );
  const [index, setIndex] = useState(0);
  const img = data?.[index];
  const length = data?.length ?? 0;
  const has = (delta: number) => Boolean(data?.[index + delta]);
  const go = (delta: number) => {
    setIndex(Math.max(0, Math.min(index + delta, length - 1)));
  };
  return (
    <Card>
      <Space vertical>
        "{series}" - id: {img?.imageId}
        {img ? (
          <>
            <img style={{ background: "white" }} src={"/web/image/" + projectId + "/" + img.imageId} />
          </>
        ) : (
          <Loading />
        )}
        <Space>
          <Button onClick={() => go(+10)} disabled={!has(1)}>
            Prev 10
          </Button>
          <Button onClick={() => go(+1)} disabled={!has(1)}>
            Prev 1
          </Button>
          <InputChangeOnEnter
            type="number"
            value={length - index}
            onChange={(x) => {
              const i = length - parseInt(x);
              if (data?.[i]) {
                setIndex(i);
              }
            }}
            style={{ width: "90px" }}
          />{" "}
          / {data?.length}
          <Button onClick={() => go(-1)} disabled={!has(-1)}>
            Next 1
          </Button>
          <Button onClick={() => go(-10)} disabled={!has(-1)}>
            Next 10
          </Button>
        </Space>
      </Space>
    </Card>
  );
};

const InputChangeOnEnter: typeof Input = memo(({ value, onChange, ...props }) => {
  const [temp, setTemp] = useState(value);
  useEffect(() => {
    setTemp(value);
  }, [value]);
  return (
    <Input
      {...props}
      value={temp}
      onChange={(x) => setTemp(x)}
      onKeyDown={(e) => {
        if (e.key == "Enter") {
          onChange?.(temp as any, e as any);
        }
      }}
    />
  );
});
