import { useParams, useSearchParams } from "react-router-dom";
import { useEffect, useMemo } from "react";
import { Divider, Progress, Space, Breadcrumb } from "@douyinfe/semi-ui";
import { ProjectContext, useProjectStatus } from "../../hooks/useProject";
import { Logs } from "../../components/project/logs/logs";
import { Actions } from "../../components/project/actions";
import { Hardware } from "../../components/project/hardware";
import { SectionTitle } from "../../components/common/sectionTitle";
import { AppTitle } from "../../components/appTitle";
import { ImagesAndScatters } from "../../components/project/imagesAndScatters";
import { getProject } from "../../services/projects";
import { RunSelect } from "../../components/project/runSelect";
import PlatformProps, { PlatformTitleJson } from "../../components/project/platformProps";
import Loading from "../../components/common/loading";
import { addNotice } from "../../utils/notification";
import { Progresses } from "../../components/project/progress";
import { IconHome } from "@douyinfe/semi-icons";

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

  // Define breadcrumb routes dynamically
  const breadcrumbRoutes = [
    {
      path: "/",
      href: "/",
      icon: <IconHome size="small" />,
    },
    {
      path: `/web/project/${projectId}`,
      href: `/web/project/${projectId}`,
      name: projectName,
    },
    runId && {
      path: `/web/project/${projectId}?run=${runId}`,
      href: `/web/project/${projectId}?run=${runId}`,
      name: runId,
    },
  ].filter(Boolean); // Remove any falsy values (e.g., when there's no runId)

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
          <Breadcrumb compact={false} routes={breadcrumbRoutes} />
        </AppTitle>
        {runId ? (
          <>
            <SectionTitle title="Logs" />
            <Logs />
            <Divider margin="10px" />
            <SectionTitle title="Progresses" />
            <Progresses />
            <Divider margin="10px" />
            <SectionTitle title="Actions" />
            <Actions />
            <Divider margin="10px" />
            <SectionTitle title="Images & Scalars" />
            <ImagesAndScatters />
            <Divider margin="10px" />
            <SectionTitle title="Hardware" />
            <Hardware />
            <Divider margin="10px" />
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
