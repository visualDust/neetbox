import {
  Button,
  Col,
  Input,
  Popover,
  Row,
  Space,
  Typography,
} from "@douyinfe/semi-ui";
import { useContext, useState } from "react";
import { ProjectStatus, getProject } from "../../../services/projects";
import { ProjectContext } from "../../../pages/console/proejctDashboard";

interface Props {
  actions: ProjectStatus["__action"];
}

export function Actions({ actions }: Props) {
  const [blocking, setBlocking] = useState(false);
  const actionList = Object.entries(actions?.value ?? {});
  return (
    <Space style={{ marginBottom: "20px" }} spacing="medium" wrap>
      {actionList.length ? (
        actionList.map(([actionName, actionOptions]) => (
          <ActionItem
            name={actionName}
            actionOptions={actionOptions}
            blocking={blocking}
            setBlocking={setBlocking}
          />
        ))
      ) : (
        <Typography.Text>
          No actions (
          <a target="_blank" href="https://neetbox.550w.host/docs/guide/">
            docs
          </a>
          )
        </Typography.Text>
      )}
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
  const [running, setCurrentBlocking] = useState(false);
  const { projectName } = useContext(ProjectContext)!;
  const handleRun = () => {
    if (options.blocking) setBlocking(true);
    setCurrentBlocking(true);
    getProject(projectName).sendAction(name, args, () => {
      if (options.blocking) setBlocking(false);
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
        {Object.entries(options.args).map(([argName, argType]) => (
          <Row
            key={argName}
            align="middle"
            type="flex"
            justify="space-between"
            style={{ alignSelf: "stretch" }}
          >
            <Col span={4}>
              <Typography.Text ellipsis>{argName}</Typography.Text>
            </Col>
            <Col span={16}>
              <Input
                size="small"
                value={args[argName]}
                onChange={(val) => setArgs({ ...args, [argName]: val })}
              />
            </Col>
            <Col span={3}>
              <Typography.Text ellipsis>({argType})</Typography.Text>
            </Col>
          </Row>
        ))}
        <Button
          style={{ width: "100px" }}
          onClick={handleRun}
          type="warning"
          theme="solid"
          disabled={blocking}
        >
          Run
        </Button>
      </Space>
    </div>
  );
  return (
    <Popover trigger="click" content={renderContent()}>
      <Button disabled={blocking && !running} loading={running}>
        {name}
      </Button>
    </Popover>
  );
}
