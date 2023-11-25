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
  const [blocking, setBlocking] = useState(false);
  return (
    <Space>
      {Object.entries(actions.value).map(([actionName, actionOptions]) => (
        <ActionItem
          name={actionName}
          actionOptions={actionOptions}
          blocking={blocking}
          setBlocking={setBlocking}
        />
      ))}
    </Space>
  );
}

interface ActionItemProps {
  name: string;
  actionOptions: ProjectStatus["__action"]["value"][string];
  blocking: boolean;
  setBlocking: (blocking: boolean) => void;
}

export function ActionItem({
  name,
  actionOptions: options,
  blocking,
  setBlocking,
}: ActionItemProps) {
  const [args, setArgs] = useState<Record<string, string>>({});
  const [currentBlocking, setCurrentBlocking] = useState(false);
  const { projectName } = useContext(ProjectContext)!;
  const handleRun = () => {
    setBlocking(true);
    setCurrentBlocking(true);
    getProject(projectName).sendAction(name, args, () => {
      setBlocking(false);
      setCurrentBlocking(false);
    });
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
        <Button
          style={{ width: "100px" }}
          onClick={handleRun}
          disabled={blocking}
        >
          Run
        </Button>
      </Space>
    </div>
  );
  return (
    <Popover trigger="click" content={renderContent()}>
      <Button disabled={blocking && !currentBlocking} loading={currentBlocking}>
        {name}
      </Button>
    </Popover>
  );
}