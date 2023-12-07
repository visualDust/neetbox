import { memo, useEffect, useMemo, useRef, useState } from "react";
import { Button, Card, Space, Typography } from "@douyinfe/semi-ui";
import { IconClose, IconMaximize } from "@douyinfe/semi-icons";
import { useCurrentProject, useProjectWebSocket } from "../../../hooks/useProject";
import { ECharts } from "../../echarts";
import { useAPI } from "../../../services/api";
import { createCondition } from "../../../utils/condition";
import Loading from "../../loading";

export const Scatters = memo(() => {
  return (
    <Space style={{ marginBottom: "20px" }}>
      <AllScatterViewers />
    </Space>
  );
});

export const AllScatterViewers = memo(() => {
  const { projectId } = useCurrentProject();
  const { data: series, mutate } = useAPI(`/series/${projectId}/scatter`);
  useProjectWebSocket(projectId, "scatter", (msg) => {
    if (msg.payload.series != null && !series.includes(msg.payload.series)) {
      mutate([...series, msg.payload.series]);
    }
  });
  return series?.map((s) => <ScatterViewer key={s} series={s} />) ?? <Loading />;
});

export const ScatterViewer = memo(({ series }: { series: string }) => {
  const { projectId, runId } = useCurrentProject();
  const { data, mutate } = useAPI(
    runId ? `/scatter/${projectId}/history?${createCondition({ series, runId })}` : null,
  );
  const [maximized, setMaximized] = useState(false);
  useProjectWebSocket(projectId, "scatter", (msg) => {
    if (series == msg.payload.series && (!runId || runId == msg.runid)) {
      if (data) {
        mutate([...data, { metadata: msg.payload }], { revalidate: false });
      }
    }
  });

  const points = data?.map((x) => x.metadata) ?? [];

  const initialOption = () => {
    return {
      backgroundColor: "transparent",
      animation: false,
      tooltip: {
        trigger: "axis",
      },
      toolbox: {
        feature: {
          dataZoom: {},
          restore: {},
          saveAsImage: {},
          dataView: {},
        },
      },
      dataZoom: [
        {
          type: "slider",
          show: true,
          xAxisIndex: [0],
        },
        // {
        //   type: "slider",
        //   show: true,
        //   yAxisIndex: [0],
        // },
        {
          type: "inside",
          xAxisIndex: [0],
        },
        // {
        //   type: "inside",
        //   yAxisIndex: [0],
        // },
      ],
      grid: {
        top: 20,
        bottom: 20,
        left: 30,
        right: 20,
      },
      xAxis: {
        type: "value",
        min: "dataMin",
        // max: "dataMax",
      },
      yAxis: [
        {
          type: "value",
          // min: "dataMin",
          // max: "dataMax",
        },
      ],
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useMemo(() => {
    const newOption = {
      series: [
        {
          name: series,
          type: "line",
          symbol: null,
          data: points?.map((x) => [x.x, x.y]),
          // sampling: "lttb",
        },
      ],
    } as echarts.EChartsOption;
    return newOption;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [points]);

  const maxBoxRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (maximized) {
      maxBoxRef.current?.focus();
    }
  }, [maximized]);

  return (
    <Card style={{ overflow: "visible", position: "relative" }}>
      <Space vertical>
        <Typography.Title heading={4}>scatter "{series}"</Typography.Title>
        <div
          style={
            maximized
              ? {
                  position: "fixed",
                  top: 0,
                  right: 0,
                  bottom: 0,
                  left: 0,
                  background: "var(--semi-color-bg-0)",
                  zIndex: 1,
                  display: "flex",
                  flexDirection: "column",
                }
              : {
                  height: "345px",
                  width: "450px",
                }
          }
          ref={maxBoxRef}
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key == "Escape") {
              setMaximized(false);
            }
          }}
        >
          {maximized && <Typography.Title heading={4}>scatter "{series}"</Typography.Title>}
          {data ? (
            <ECharts
              initialOption={initialOption}
              updatingOption={updatingOption}
              style={{ width: "100%", height: "100%", flex: 1 }}
            />
          ) : (
            <Loading height="100%" width="100%" />
          )}
          {maximized && (
            <Button
              icon={<IconClose />}
              style={{ position: "absolute", right: 10, top: 0 }}
              onClick={() => setMaximized(false)}
            />
          )}
        </div>
      </Space>
      <Button
        icon={<IconMaximize />}
        style={{ position: "absolute", right: 20, top: 15 }}
        onClick={() => setMaximized(true)}
      />
    </Card>
  );
});
