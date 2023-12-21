import { useParams, useSearchParams } from "react-router-dom";
import { useEffect, useMemo } from "react";
import { Divider, Progress, Space } from "@douyinfe/semi-ui";
import { ProjectContext, useProjectStatus } from "../../hooks/useProject";
import { Logs } from "../../components/dashboard/project/logs/logs";
import { Actions } from "../../components/dashboard/project/actions";
import { Hardware } from "../../components/dashboard/project/hardware";
import { SectionTitle } from "../../components/sectionTitle";
import { AppTitle } from "../../components/appTitle";
import { ImagesAndScatters } from "../../components/dashboard/project/imagesAndScatters";
import { getProject } from "../../services/projects";
import { RunSelect } from "../../components/dashboard/project/runSelect";
import PlatformProps, { PlatformTitleJson } from "../../components/dashboard/project/platformProps";
import Loading from "../../components/loading";
import { addNotice } from "../../utils/notification";
import { Progresses } from "../../components/dashboard/project/progress";

export default function ProjectDashboardButRecreateOnRouteChange() {
  const { projectId } = useParams();
  return <ProjectDashboard key={projectId} />;
}

function ProjectDashboard() {
  const { projectId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  if (!projectId) throw new Error("projectId required");

  const { data: status, mutate } = useProjectStatus(projectId);
  const projectName = status?.name ?? projectId;

  useEffect(() => {
    if (projectName) {
      getProject(projectId).name = projectName;
    }
  }, [projectId, projectName]);

  const runIds = status?.runids;
  const lastRunId = runIds ? runIds[runIds.length - 1] : undefined;
  const paramRun = searchParams.get("run");
  const paramRunFound = runIds?.find((x) => x.runId == paramRun);
  const runInfo = paramRunFound ?? lastRunId;
  const runId = runInfo?.runId;
  const isOnlineRun = Boolean(runInfo?.online);

  useEffect(() => {
    if (runIds && paramRun && !paramRunFound) {
      addNotice({
        type: "error",
        title: `Can not find run "${paramRun}"`,
        content: "Showing the latest run",
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [!!runIds, paramRun, paramRunFound]);

  const setRunId = (id: string) => {
    if (id === lastRunId.runId) {
      setSearchParams({});
    } else {
      setSearchParams({ run: id });
    }
  };

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
              <RunSelect {...{ setRunId, runIds, mutateRunIds: mutate, projectId, runId, isOnlineRun }} />
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
            <SectionTitle title="Progresses" />
            <Progresses />
            <Divider />
            <SectionTitle title="Actions" />
            <Actions />
            <Divider />
            <SectionTitle title="Images & Scalars" />
            <ImagesAndScatters />
            <Divider />
            <SectionTitle title="Hardware" />
            <Hardware />
            <Divider />
            <SectionTitle
              title={
                <Space>
                  Platform
                  <PlatformTitleJson />
                </Space>
              }
            />
            <PlatformProps />
          </>
        ) : (
          <Loading size="large" height="70vh" />
        )}
      </div>
    </ProjectContext.Provider>
  );
}
