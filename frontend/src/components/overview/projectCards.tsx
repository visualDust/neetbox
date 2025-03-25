import { Button, Card, CardGroup, Toast, Typography, Descriptions, Tag } from "@douyinfe/semi-ui";
import { IconCloud, IconGlobeStroke, IconCopy } from "@douyinfe/semi-icons";
import React, { memo } from "react";
import { useNavigate } from "react-router-dom";
import { useAPI } from "../../services/api";

interface ProjectProps {
  projectId: string;
  name: string;
  storage: number;
  online: boolean;
  runids: any[];
}

export const ProjectCard = memo(({ project }: { project: ProjectProps }) => {
  const navigate = useNavigate();
  return (
    <Card
      shadows="hover"
      title={project.name}
      headerLine={true}
      headerStyle={{ padding: "10px" }}
      bodyStyle={{
        padding: "10px",
        minHeight: "50px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        textAlign: "center",
      }}
      //if online, make it green, if offline, make it red
      style={{ width: 260 }}
      headerExtraContent={
        <Button
          icon={<IconCopy />}
          style={{ marginRight: 10 }}
          size="small"
          onClick={() => {
            navigator.clipboard.writeText(project.projectId).then(
              () => {
                // copy success
                Toast.info("Copied project id to clipboard");
              },
              () => {
                // copy failed
                Toast.error("Failed to copy");
              },
            );
          }}
        ></Button>
      }
    >
      <Descriptions
        data={[
          {
            key: (
              <div>
                {project.online ? (
                  <Tag style={{ marginLeft: "10px" }} color="green">
                    Online
                  </Tag>
                ) : (
                  <Tag style={{ marginLeft: "10px" }} color="red">
                    Offline
                  </Tag>
                )}
              </div>
            ),
            value: <div>Log size {(project.storage / 1e6).toFixed(2)} MB</div>,
          },
        ]}
      />

      <Button
        icon={project.online ? <IconGlobeStroke /> : <IconCloud />}
        style={{ marginRight: 10 }}
        onClick={() => {
          navigate(`/project/${project.projectId}`); // Assuming you have a navigate function to handle routing
        }}
      >
        {project.online ? "Open Dashboard" : `View ${project.runids.length} Runs`}
      </Button>
    </Card>
  );
});

export function ProjectCards() {
  const { data } = useAPI("/project/list", { refreshInterval: 5000 });
  return (
    <div>
      <CardGroup spacing={10}>
        {data ? (
          data.map((project: ProjectProps) => <ProjectCard key={project.projectId} project={project} />)
        ) : (
          <Card style={{ width: 260, height: 150, textAlign: "center" }}>Loading...</Card>
        )}
      </CardGroup>
    </div>
  );
}
