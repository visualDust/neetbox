import {
  Button,
  Col,
  Input,
  Popover,
  Row,
  Space,
  Typography,
} from "@douyinfe/semi-ui";
import { ProjectStatus, getProject } from "../../../services/projects";
import { useContext, useState } from "react";
import { ProjectContext } from "../../../pages/console/proejctDashboard";

interface Props {
  actions: ProjectStatus["__action"];
}

export function Actions({ actions }: Props) {
  return (
    <Space>
      {Object.entries(actions.value).map(([actionName, actionOptions]) => (
        <ActionItem name={actionName} actionOptions={actionOptions} />
      ))}
    </Space>
  );
}

export function ActionItem({
  name,
  actionOptions: options,
}: {
  name: string;
  actionOptions: ProjectStatus["__action"]["value"][string];
}) {
  const [args, setArgs] = useState<Record<string, string>>({});
  const { projectName } = useContext(ProjectContext)!;
  const handleRun = () => {
    getProject(projectName).sendAction(name, args);
  };
  const renderContent = () => (
    <div style={{ padding: "10px", maxWidth: "400px" }}>
      <Space vertical spacing={"tight"}>
        <Typography.Title heading={5}>{name}</Typography.Title>
        {options.description && (
          <div style={{ margin: 0, whiteSpace: "pre-wrap" }}>
            {options.description}
          </div>
        )}
        {options.args.map((argName) => (
          <Row align="middle" style={{ alignSelf: "stretch" }}>
            <Col span={6}>
              <Typography.Text ellipsis>{argName}</Typography.Text>
            </Col>
            <Col span={18}>
              <Input
                size="small"
                value={args[argName]}
                onChange={(val) => setArgs({ ...args, [argName]: val })}
              />
            </Col>
          </Row>
        ))}
        <Button style={{ width: "100px" }} onClick={handleRun}>
          Run
        </Button>
      </Space>
    </div>
  );
  return (
    <Popover trigger="click" content={renderContent()}>
      <Button>{name}</Button>
    </Popover>
  );
}
