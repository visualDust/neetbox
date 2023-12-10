import { memo, useEffect, useState } from "react";
import { Button, Card, Input, Popover, Space, Typography } from "@douyinfe/semi-ui";
import { IconDownload } from "@douyinfe/semi-icons";
import { useCurrentProject, useProjectData, useProjectSeries } from "../../../hooks/useProject";
import Loading from "../../loading";
import { CenterBox } from "../../centerBox";

export const Images = memo(() => {
  return (
    <Space style={{ marginBottom: "20px" }}>
      <AllImageViewers />
    </Space>
  );
});

export const AllImageViewers = memo(() => {
  const { projectId } = useCurrentProject()!;
  const series = useProjectSeries(projectId, "image");
  return series?.map((s) => <SeriesViewer key={s} series={s} />) ?? <Loading text="Images loading" />;
});

const SeriesViewer = memo(({ series }: { series: string }) => {
  const { projectId, runId } = useCurrentProject()!;
  const data = useProjectData({
    type: "image",
    disable: !runId,
    projectId,
    runId,
    conditions: {
      series,
    },
    limit: 1000,
    transformHTTP: (x) => ({ id: x.imageId, ...JSON.parse(x.metadata) }),
    transformWS: (x) => ({ ...x, ...x.payload }),
    filterWS: (x) => x.payload.series == series,
    onNewWSData: () => {
      if (index == length - 1) setIndex((i) => i + 1);
    },
  });
  const [realIndex, setIndex] = useState(-1);
  const length = data?.length ?? 0;
  const index = realIndex < 0 ? length - 1 : realIndex;
  const img = data?.[index];
  const has = (delta: number) => Boolean(data?.[index + delta]);
  const move = (delta: number) => {
    goto(Math.max(0, Math.min(index + delta, length - 1)));
  };
  const goto = (newIndex: number) => setIndex(newIndex == length - 1 ? -1 : newIndex);
  const imgSrc = img ? `/web/image/${projectId}/${img.id}` : null;
  return (
    <Card bodyStyle={{ position: "relative" }}>
      <Space vertical>
        <Typography.Title heading={4}>image "{series}"</Typography.Title>
        <Popover position="top" content={<Button disabled>Batch Download (WIP)</Button>}>
          <a
            href={imgSrc!}
            target="_blank"
            download
            style={{ position: "absolute", top: "15px", right: "20px" }}
          >
            <Button icon={<IconDownload />} />
          </a>
        </Popover>
        {img ? (
          <a href={imgSrc!} target="_blank" style={{ display: "block", position: "relative" }}>
            <img
              style={{ background: "white", objectFit: "contain", width: "450px", height: "300px" }}
              src={imgSrc!}
            />
          </a>
        ) : data && !data.length ? (
          <CenterBox style={{ width: "450px", height: "300px" }}>
            <Typography.Text type="tertiary">No image</Typography.Text>
          </CenterBox>
        ) : (
          <Loading width="450px" height="300px" />
        )}
        <Space>
          <Button onClick={() => move(-10)} disabled={!has(-1)}>
            {"<<"}
          </Button>
          <Button onClick={() => move(-1)} disabled={!has(-1)}>
            {"<"}
          </Button>
          <InputChangeOnEnter
            type="text"
            value={index + 1}
            onChange={(x) => {
              const i = parseInt(x) - 1;
              if (data?.[i]) {
                goto(i);
              }
            }}
            style={{ width: "60px" }}
          />{" "}
          / {data?.length ?? "..."}
          <Button onClick={() => move(+1)} disabled={!has(1)}>
            {">"}
          </Button>
          <Button onClick={() => move(+10)} disabled={!has(1)}>
            {">>"}
          </Button>
        </Space>
      </Space>
    </Card>
  );
});

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
          onChange?.(temp as any, null!);
        }
      }}
    />
  );
});
