import { useParams } from "react-router-dom";
import { useMemo } from "react";
import { Divider } from "@douyinfe/semi-ui";
import PlatformProps from "../../components/dashboard/project/platformProps";
import { ProjectContext, useProjectStatus } from "../../hooks/useProject";
import { Logs } from "../../components/dashboard/project/logs/logs";
import { Actions } from "../../components/dashboard/project/actions";
import Loading from "../../components/loading";
import { Hardware } from "../../components/dashboard/project/hardware";
import { SectionTitle } from "../../components/sectionTitle";
import { Images } from "../../components/dashboard/project/images";
import { AppTitle } from "../../components/appTitle";
import { Scatters } from "../../components/dashboard/project/scatters";

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

  const projectContextData = useMemo(
    () => ({
      projectId,
      projectName,
    }),
    [projectId, projectName],
  );

  return (
    <ProjectContext.Provider value={projectContextData}>
      <div style={{ padding: "20px" }}>
        <AppTitle>Project "{projectName ?? projectId}"</AppTitle>
        <SectionTitle title="Logs" />
        <Logs />
        <SectionTitle title="Images" />
        <Images />
        <SectionTitle title="Scatters" />
        <Scatters />
        <Divider />
        {data.current ? (
          <>
            <SectionTitle title="Actions" />
            <Actions actions={data.current.__action} />
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
