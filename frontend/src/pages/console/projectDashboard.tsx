import { useParams, useSearchParams } from "react-router-dom";
import { useEffect, useMemo } from "react";
import { Divider } from "@douyinfe/semi-ui";
import { ProjectContext, useProjectRunIds, useProjectStatus } from "../../hooks/useProject";
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
import { addNotice } from "../../utils/notification";

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
  const lastRunId = runIds ? runIds[runIds.length - 1].id : undefined;
  const paramRun = searchParams.get("run");
  const paramRunFound = runIds?.find((x) => x.id == paramRun)?.id;
  const runId = paramRunFound ?? lastRunId;
  const projectOnline = Boolean(status?.online);
  const isOnlineRun = Boolean(runId && runId == lastRunId && status?.online);

  useEffect(() => {
    if (paramRun && !paramRunFound) {
      addNotice({
        type: "error",
        title: `Can not find run "${paramRun}"`,
        content: "Showing the latest run",
      });
    }
  }, [paramRun, paramRunFound]);

  const setRunId = (id: string) => {
    if (id === lastRunId) {
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
      projectOnline,
    }),
    [projectId, projectName, runId, isOnlineRun, projectOnline],
  );

  return (
    <ProjectContext.Provider value={projectContextData}>
      <div style={{ padding: "20px", position: "relative" }}>
        <AppTitle
          extra={
            <ProjectContext.Provider key={projectId} value={projectContextData}>
              <RunSelect
                {...{ setRunId, runIds, mutateRunIds: mutate, projectId, runId, isOnlineRun, projectOnline }}
              />
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
