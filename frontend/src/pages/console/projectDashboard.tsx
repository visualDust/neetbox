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

  const [runId, setRunId] = useState<string | undefined>(undefined);

  const projectContextData = useMemo(
    () => ({
      projectId,
      projectName,
      runId,
      setRunId,
    }),
    [projectId, projectName, runId],
  );

  return (
    <ProjectContext.Provider value={projectContextData}>
      <div style={{ padding: "20px", position: "relative" }}>
        <AppTitle
          extra={
            <ProjectContext.Provider key={projectId} value={projectContextData}>
              <RunSelect />
            </ProjectContext.Provider>
          }
        >
          Project "{projectName ?? projectId}"
        </AppTitle>
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
        {/* {data.current ? (
          <>
            <SectionTitle title="Platform" />
            <PlatformProps data={data.current.platform} />
          </>
        ) : (
          <Loading size="large" />
        )} */}
      </div>
    </ProjectContext.Provider>
  );
}
