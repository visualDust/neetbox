import { useParams } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { Divider } from "@douyinfe/semi-ui";
import { ProjectContext, useProjectStatus } from "../../hooks/useProject";
import { Logs } from "../../components/dashboard/project/logs/logs";
import { Actions } from "../../components/dashboard/project/actions";
import { Hardware } from "../../components/dashboard/project/hardware";
import { SectionTitle } from "../../components/sectionTitle";
import { AppTitle } from "../../components/appTitle";
import { ImagesAndScatters } from "../../components/dashboard/project/imagesAndScatters";
import { getProject } from "../../services/projects";
import { RunSelect } from "../../components/dashboard/project/runSelect";
import PlatformProps from "../../components/dashboard/project/platformProps";
import Loading from "../../components/loading";
import { useAPI } from "../../services/api";

export default function ProjectDashboardButRecreateOnRouteChange() {
  const { projectId } = useParams();
  return <ProjectDashboard key={projectId} />;
}

function ProjectDashboard() {
  const { projectId } = useParams();
  if (!projectId) throw new Error("projectId required");

  const status = useProjectStatus(projectId);
  const projectName = status?.name ?? projectId;

  useEffect(() => {
    if (projectName) {
      getProject(projectId).name = projectName;
    }
  }, [projectId, projectName]);

  const { data: runIds } = useAPI(`/runids/${projectId}`, { refreshInterval: 5000 });
  const [runId, setRunId] = useState<string | undefined>(undefined);

  const lastRunId = runIds ? runIds[runIds.length - 1].id : undefined;
  useEffect(() => {
    if (runId === undefined && lastRunId) {
      setRunId(lastRunId);
    }
  }, [lastRunId, runId, setRunId]);

  const isOnlineRun = Boolean(runId && runId == lastRunId && status.online);

  const projectContextData = useMemo(
    () => ({
      projectId,
      projectName,
      runId,
      isOnlineRun,
    }),
    [projectId, projectName, runId, isOnlineRun],
  );

  return (
    <ProjectContext.Provider value={projectContextData}>
      <div style={{ padding: "20px", position: "relative" }}>
        <AppTitle
          extra={
            <ProjectContext.Provider key={projectId} value={projectContextData}>
              <RunSelect runIds={runIds} setRunId={setRunId} />
            </ProjectContext.Provider>
          }
        >
          Project "{projectName ?? projectId}"
        </AppTitle>
        {runId ? (
          <>
            <SectionTitle title="Logs" />
            <Logs />
            <Divider />
            <SectionTitle title="Actions" />
            <Actions />
            <Divider />
            <SectionTitle title="Images & Scalars" />
            <ImagesAndScatters />
            {/* <SectionTitle title="Images" />
        <Images /> */}
            {/* <SectionTitle title="Scatters" />
        <Scatters /> */}
            <Divider />
            <SectionTitle title="Hardware" />
            <Hardware />
            <Divider />
            <SectionTitle title="Platform" />
            <PlatformProps />
          </>
        ) : (
          <Loading size="large" height="70vh" />
        )}
      </div>
    </ProjectContext.Provider>
  );
}
