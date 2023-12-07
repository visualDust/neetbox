import { useParams } from "react-router-dom";
import { useMemo, useState } from "react";
import { Divider, Select, Space, Typography } from "@douyinfe/semi-ui";
import PlatformProps from "../../components/dashboard/project/platformProps";
import { ProjectContext, useProjectStatus } from "../../hooks/useProject";
import { Logs } from "../../components/dashboard/project/logs/logs";
import { Actions } from "../../components/dashboard/project/actions";
import Loading from "../../components/loading";
import { Hardware } from "../../components/dashboard/project/hardware";
import { SectionTitle } from "../../components/sectionTitle";
import { AppTitle } from "../../components/appTitle";
import { ImagesAndScatters } from "../../components/dashboard/project/imagesAndScatters";
import { useAPI } from "../../services/api";

export default function ProjectDashboardButRecreateOnRouteChange() {
  const { projectId } = useParams();
  return <ProjectDashboard key={projectId} />;
}

function ProjectDashboard() {
  const { projectId } = useParams();
  if (!projectId) throw new Error("projectId required");

  const data = useProjectStatus(projectId);
  // console.info("project", { projectId, data });

  const projectName = data.current?.config.value.name;

  const { data: runIds } = useAPI(`/runids/${projectId}`);
  const [runId, setRunId] = useState<string | undefined>(undefined);

  const projectContextData = useMemo(
    () => ({
      projectId,
      projectName,
      runId,
    }),
    [projectId, projectName, runId],
  );

  return (
    <ProjectContext.Provider value={projectContextData}>
      <div style={{ padding: "20px", position: "relative" }}>
        <AppTitle
          extra={
            <Space>
              Run:
              <Select value={runId} onChange={(x) => setRunId(x as any)}>
                <Select.Option value={undefined}>All</Select.Option>
                {[...(runIds ?? [])].reverse().map((x) => (
                  <Select.Option value={x.id}>
                    {x.timestamp} <Typography.Text type="tertiary">({x.id})</Typography.Text>
                  </Select.Option>
                ))}
              </Select>
            </Space>
          }
        >
          Project "{projectName ?? projectId}"
        </AppTitle>
        <SectionTitle title="Logs" />
        <Logs />
        <SectionTitle title="Actions" />
        {data.current ? <Actions actions={data.current.__action} /> : <Loading size="large" />}
        <SectionTitle title="Images & Scatters" />
        <ImagesAndScatters />
        {/* <SectionTitle title="Images" />
        <Images /> */}
        {/* <SectionTitle title="Scatters" />
        <Scatters /> */}
        <Divider />
        {data.current ? (
          <>
            <Divider />
            <SectionTitle title="Hardware" />
            <Hardware hardwareData={data.history.map((x) => x.hardware)} />
            <Divider />
            <SectionTitle title="Platform" />
            <PlatformProps data={data.current.platform} />
          </>
        ) : (
          <Loading size="large" />
        )}
      </div>
    </ProjectContext.Provider>
  );
}
