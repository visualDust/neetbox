import { useParams } from "react-router-dom";
import { createContext, useMemo } from "react";
import { Typography } from "@douyinfe/semi-ui";
import PlatformProps from "../../components/dashboard/project/platformProps";
import { useProjectStatus } from "../../services/projects";
import { Logs } from "../../components/dashboard/project/logs/logs";
import { Actions } from "../../components/dashboard/project/actions";
import Loading from "../../components/loading";
import { Hardware } from "../../components/dashboard/project/hardware";

export const ProjectContext = createContext<{ projectName: string } | null>(
  null,
);

export default function ProjectDashboardButRecreateOnRouteChange() {
  const { projectName } = useParams();
  return <ProjectDashboard key={projectName} />;
}

function ProjectDashboard() {
  const { projectName } = useParams();
  if (!projectName) throw new Error("projectName required");

  const data = useProjectStatus(projectName);
  console.info("project", { projectName, data });

  const projectContextData = useMemo(
    () => ({
      projectName,
    }),
    [projectName],
  );

  return (
    <ProjectContext.Provider value={projectContextData}>
      <div style={{ padding: "10px" }}>
        <Typography.Title heading={2} style={{ textAlign: "center" }}>
          Project "{projectName}"
        </Typography.Title>
        <Typography.Title heading={3}>Logs</Typography.Title>
        <Logs projectName={projectName} />
        {data.current ? (
          <>
            <Typography.Title heading={3}>Actions</Typography.Title>
            <Actions actions={data.current.__action} />
            <Typography.Title heading={3}>Hardware</Typography.Title>
            <Hardware hardwareData={data.history.map((x) => x.hardware)} />
            <Typography.Title heading={3}>Platform</Typography.Title>
            <PlatformProps data={data.current.platform} />
          </>
        ) : (
          <Loading />
        )}
      </div>
    </ProjectContext.Provider>
  );
}
