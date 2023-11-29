import { useParams } from "react-router-dom";
import { createContext, useMemo } from "react";
import { Divider, Typography } from "@douyinfe/semi-ui";
import PlatformProps from "../../components/dashboard/project/platformProps";
import { useProjectStatus } from "../../hooks/useProject";
import { Logs } from "../../components/dashboard/project/logs/logs";
import { Actions } from "../../components/dashboard/project/actions";
import Loading from "../../components/loading";
import { Hardware } from "../../components/dashboard/project/hardware";
import { SectionTitle } from "../../components/sectionTitle";

export const ProjectContext = createContext<{ projectName: string } | null>(null);

export default function ProjectDashboardButRecreateOnRouteChange() {
  const { projectName } = useParams();
  return <ProjectDashboard key={projectName} />;
}

function ProjectDashboard() {
  const { projectName } = useParams();
  if (!projectName) throw new Error("projectName required");

  const data = useProjectStatus(projectName);
  // console.info("project", { projectName, data });

  const projectContextData = useMemo(
    () => ({
      projectName,
    }),
    [projectName],
  );

  return (
    <ProjectContext.Provider value={projectContextData}>
      <div style={{ padding: "20px" }}>
        <Typography.Title heading={2} style={{ textAlign: "center" }}>
          Project "{projectName}"
        </Typography.Title>
        <SectionTitle title="Logs" />
        <Logs projectName={projectName} />
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
