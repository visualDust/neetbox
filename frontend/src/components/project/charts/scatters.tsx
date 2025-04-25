import { memo, useCallback, useEffect, useRef, useState } from "react";
import { Button, Card, Modal, Space, Typography } from "@douyinfe/semi-ui";
import { IconClose, IconMaximize } from "@douyinfe/semi-icons";
import { useCurrentProject, useProjectData, useProjectSeries } from "../../../hooks/useProject";
import { ECharts, getSemiColorDataHexColors } from "../../common/echarts";
import Loading from "../../common/loading";

export const Scatters = memo(() => {
  return (
    <Space style={{ marginBottom: "20px" }}>
      <AllScatterViewers />
    </Space>
  );
});

export const AllScatterViewers = memo(() => {
  const { projectId, runId } = useCurrentProject();
  const series = useProjectSeries(projectId, runId!, "scalar");
  return (
    series?.map((s) => <ScatterViewer key={s} series={s} />) ?? <Loading text="Scalars loading" vertical />
  );
});

export const ScatterViewer = memo(({ series }: { series: string }) => {
  const { projectId, runId } = useCurrentProject();
  const [maximized, setMaximized] = useState(false);
  const points = useProjectData({
    type: "scalar",
    projectId,
    runId,
    conditions: { series },
    transformWS: (x) => ({ id: x.id, x: x.payload.x, y: x.payload.y }),
    transformHTTP: (x) => ({ id: x.id, x: x.metadata.x, y: x.metadata.y }),
  });
  const [hadZoom, setHadZoom] = useState<string | null>(null);
  const dataZoomOption = (init = false) => {
    if (points && points.length > 1000 && (init || hadZoom !== runId)) {
      setHadZoom(runId!);
      return { start: 90 };
    }
  };

  const initialOption = () => {
    return {
      color: getSemiColorDataHexColors(true),
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
          ...dataZoomOption(true),
        },
        // {
        //   type: "slider",
        //   show: true,
        //   yAxisIndex: [0],
        // },
        {
          type: "inside",
          xAxisIndex: [0],
          ...dataZoomOption(true),
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

  const updatingOption = useCallback(() => {
    const newOption = {
      series: [
        {
          name: series,
          type: "line",
          symbol: null,
          data: points?.map((x) => [x.x, x.y]),
          // sampling: "lttb",
          large: true,
        },
      ],
      dataZoom: [{ ...dataZoomOption() }, { ...dataZoomOption() }],
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
    <>
      <Card style={{ overflow: "visible", position: "relative" }}>
        <Space vertical>
          <Typography.Title heading={4}>scalar "{series}"</Typography.Title>
          <div style={{ height: "345px", width: "450px" }} tabIndex={0}>
            {points ? (
              <ECharts
                initialOption={initialOption}
                updatingOption={updatingOption}
                style={{ width: "100%", height: "100%", flex: 1 }}
              />
            ) : (
              <Loading height="100%" width="100%" />
            )}
          </div>
        </Space>
        <Button
          icon={<IconMaximize />}
          style={{ position: "absolute", right: 20, top: 15 }}
          onClick={() => setMaximized(true)}
        />
      </Card>
      <Modal
        fullScreen
        visible={maximized}
        className="scatters-fullscreen-modal"
        onCancel={() => setMaximized(false)}
        bodyStyle={{ height: "100%" }}
        footer={
          <Button icon={<IconClose />} onClick={() => setMaximized(false)}>
            Close(Esc)
          </Button>
        }
        zIndex={1000}
      >
        <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
          <div style={{ display: "flex", justifyContent: "center", padding: "10px" }}>
            <Typography.Title heading={3}>scalar "{series}"</Typography.Title>
          </div>
          <div style={{ flexGrow: 1 }}>
            {points ? (
              <ECharts
                initialOption={initialOption}
                updatingOption={updatingOption}
                style={{ width: "100%", height: "100%" }}
              />
            ) : (
              <Loading height="100%" width="100%" />
            )}
          </div>
        </div>
      </Modal>
    </>
  );
});
