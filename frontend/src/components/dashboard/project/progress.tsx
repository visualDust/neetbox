import { memo } from "react";
import { Button, Card, Progress, Space, Typography } from "@douyinfe/semi-ui";
import { useCurrentProject, useProjectData, useProjectSeries } from "../../../hooks/useProject";
import Loading from "../../loading";

export const Progresses = memo(() => {
  return (
    <Space style={{ marginBottom: "20px" }}>
      <AllProgressViewers />
    </Space>
  );
});

export const AllProgressViewers = memo(() => {
  const { projectId, runId } = useCurrentProject();
  const series = useProjectSeries(projectId, runId!, "progress");
  return (
    series?.map((s) => <ProgressViewer key={s} series={s} />) ?? <Loading text="Progress loading" vertical />
  );
});

export const ProgressViewer = memo(({ series }: { series: string }) => {
  const { projectId, runId } = useCurrentProject();
  const progressData = useProjectData({
    type: "progress",
    projectId,
    runId,
    conditions: { series },
    transformWS: (x) => ({
      id: x.id,
      timestamp: x.timestamp,
      ...x.payload,
    }),
    transformHTTP: (x) => ({
      id: x.id,
      timestamp: x.timestamp,
      ...x.metadata,
    }),
  });
  const lastProgressData = progressData?.at(-1);
  if (lastProgressData == undefined) return <Loading />;
  const percentage =
    lastProgressData.total == null ? 100 : Math.round((100 * lastProgressData.step) / lastProgressData.total);

  return (
    <Card
      shadows="hover"
      title={lastProgressData.name}
      headerLine={true}
      headerStyle={{ padding: "10px" }}
      bodyStyle={{
        padding: "10px",
        minHeight: "50px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
      }}
      style={{ width: 260 }}
      headerExtraContent={
        <Typography.Text>
          {lastProgressData.rate == -1 ? "N/A" : lastProgressData.rate.toFixed(5)} iter/s
        </Typography.Text>
      }
    >
      <Typography.Text>current iter {lastProgressData.current}</Typography.Text>
      <Typography.Text>
        step {lastProgressData.step}/{lastProgressData.total == null ? "unknown" : lastProgressData.total}
      </Typography.Text>
      <Typography.Text>launched at {lastProgressData.timestamp}</Typography.Text>
      <Progress
        percent={percentage}
        showInfo={true}
        style={{ height: "8px" }}
        aria-label="progress percentage"
      />
    </Card>
  );
});
