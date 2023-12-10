import { memo, useEffect, useState } from "react";
import { Button, Card, Input, Popover, Space, Typography } from "@douyinfe/semi-ui";
import { IconDownload } from "@douyinfe/semi-icons";
import { useCurrentProject, useProjectData, useProjectWebSocket } from "../../../hooks/useProject";
import { useAPI } from "../../../services/api";
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
  const { data: series, mutate } = useAPI(`/series/${projectId}/image`);
  useProjectWebSocket(projectId, "image", (msg) => {
    //@ts-expect-error TODO
    const newSeries = msg.payload.series;
    if (newSeries != null && series && !series.includes(newSeries)) {
      mutate([...series, newSeries]);
    }
  });
  return series?.map((s) => <SeriesViewer key={s} series={s} />) ?? <Loading text="Images loading" />;
});

const SeriesViewer = memo(({ series }: { series: string }) => {
  const { projectId, runId } = useCurrentProject()!;
  const data = useProjectData({
    type: "image",
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
  const [index, setIndex] = useState(0);
  const img = data?.[index];
  const length = data?.length ?? 0;
  const has = (delta: number) => Boolean(data?.[index + delta]);
  const go = (delta: number) => {
    setIndex(Math.max(0, Math.min(index + delta, length - 1)));
  };
  useEffect(() => {
    if (length > 0) {
      setIndex(length - 1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [length > 0]);
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
          <Button onClick={() => go(-10)} disabled={!has(-1)}>
            {"<<"}
          </Button>
          <Button onClick={() => go(-1)} disabled={!has(-1)}>
            {"<"}
          </Button>
          <InputChangeOnEnter
            type="text"
            value={index + 1}
            onChange={(x) => {
              const i = parseInt(x) - 1;
              if (data?.[i]) {
                setIndex(i);
              }
            }}
            style={{ width: "60px" }}
          />{" "}
          / {data?.length ?? "..."}
          <Button onClick={() => go(+1)} disabled={!has(1)}>
            {">"}
          </Button>
          <Button onClick={() => go(+10)} disabled={!has(1)}>
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
