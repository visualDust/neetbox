import { memo, useEffect, useState } from "react";
import { Button, Card, Input, Popover, Space, Typography } from "@douyinfe/semi-ui";
import { IconDownload } from "@douyinfe/semi-icons";
import { useCurrentProject, useProjectWebSocket } from "../../../hooks/useProject";
import { useAPI } from "../../../services/api";
import Loading from "../../loading";
import { createCondition } from "../../../utils/condition";

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
    const newSeries = msg.metadata.series;
    if (newSeries != null && !series.includes(newSeries)) {
      mutate([...series, newSeries]);
    }
  });
  return series?.map((s) => <SeriesViewer key={s} series={s} />) ?? <Loading />;
});

const SeriesViewer = memo(({ series }: { series: string }) => {
  const { projectId } = useCurrentProject()!;
  const { data, mutate } = useAPI(
    `/image/${projectId}/history?${createCondition({
      series,
      limit: 1000,
      order: {
        id: "DESC",
      },
    })}`,
  );
  const [index, setIndex] = useState(0);
  useProjectWebSocket(projectId, "image", (msg) => {
    if (msg.metadata.series === series) {
      mutate([msg, ...data], { revalidate: false });
      if (index > 0) {
        setIndex((i) => i + 1);
      }
    }
  });
  const img = data?.[index];
  const length = data?.length ?? 0;
  const has = (delta: number) => Boolean(data?.[index + delta]);
  const go = (delta: number) => {
    setIndex(Math.max(0, Math.min(index + delta, length - 1)));
  };
  const imgSrc = img ? `/web/image/${projectId}/${img.imageId}` : null;
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
              style={{ background: "white", objectFit: "contain", width: "400px", height: "300px" }}
              src={imgSrc!}
            />
          </a>
        ) : (
          <Loading width="400px" height="300px" />
        )}
        <Space>
          <Button onClick={() => go(+10)} disabled={!has(1)}>
            {"<<"}
          </Button>
          <Button onClick={() => go(+1)} disabled={!has(1)}>
            {"<"}
          </Button>
          <InputChangeOnEnter
            type="text"
            value={length - index}
            onChange={(x) => {
              const i = length - parseInt(x);
              if (data?.[i]) {
                setIndex(i);
              }
            }}
            style={{ width: "60px" }}
          />{" "}
          / {data?.length}
          <Button onClick={() => go(-1)} disabled={!has(-1)}>
            {">"}
          </Button>
          <Button onClick={() => go(-10)} disabled={!has(-1)}>
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
