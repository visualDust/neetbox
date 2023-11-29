import { Button, Checkbox, Col, Input, Popover, Row, Space, Typography } from "@douyinfe/semi-ui";
import { memo, useContext, useState } from "react";
import { IconChevronDown, IconPlay } from "@douyinfe/semi-icons";
import { ProjectStatus, getProject } from "../../../services/projects";
import { ProjectContext } from "../../../pages/console/proejctDashboard";
import { useMemoJSON } from "../../../hooks/useMemoJSON";

interface Props {
  actions: ProjectStatus["__action"];
}

export function Actions({ actions }: Props) {
  const [blocking, setBlocking] = useState(false);
  const actionList = Object.entries(useMemoJSON(actions?.value ?? {}));
  return (
    <Space style={{ marginBottom: "20px" }} spacing="medium" wrap>
      {actionList.length ? (
        actionList.map(([actionName, actionOptions]) => (
          <ActionItem
            key={actionName}
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

export const ActionItem = memo(({ name, actionOptions: options, blocking, setBlocking }: ActionItemProps) => {
  const [args, setArgs] = useState<Record<string, string>>(() =>
    Object.fromEntries(
      Object.entries(options.args).map(([name, type]) => [
        name,
        type == "str" ? '""' : type == "bool" ? "False" : "",
      ]),
    ),
  );
  const [running, setCurrentBlocking] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const { projectName } = useContext(ProjectContext)!;
  const handleRun = () => {
    if (options.blocking) setBlocking(true);
    setCurrentBlocking(true);
    getProject(projectName).sendAction(name, args, ({ error: err, result: res }) => {
      if (options.blocking) setBlocking(false);
      setCurrentBlocking(false);
      setResult(err ? `error:\n${err}` : `result:\n${JSON.stringify(res)}`);
    });
  };
  const renderContent = () => (
    <Space vertical spacing={"tight"} style={{ padding: "10px", minWidth: "200px", maxWidth: "500px" }}>
      <Typography.Title heading={5}>{name}</Typography.Title>
      {options.description && <div style={{ margin: 0, whiteSpace: "pre-wrap" }}>{options.description}</div>}
      {Object.entries(options.args).map(([argName, argType]) => (
        <Row
          key={argName}
          align="middle"
          type="flex"
          justify="space-between"
          style={{ alignSelf: "stretch" }}
        >
          <Col span={6}>
            <Typography.Text ellipsis={{ showTooltip: true }}>{argName}</Typography.Text>
          </Col>
          <Col span={12}>
            {argType == "bool" ? (
              <Checkbox
                checked={args[argName] == "True"}
                onChange={() =>
                  setArgs({
                    ...args,
                    [argName]: args[argName] == "True" ? "False" : "True",
                  })
                }
              >
                {args[argName]}
              </Checkbox>
            ) : (
              <Input
                size="small"
                value={args[argName]}
                onChange={(val) => setArgs({ ...args, [argName]: val })}
              />
            )}
          </Col>
          <Col span={6}>
            <Typography.Text ellipsis={{ showTooltip: true }}>({argType})</Typography.Text>
          </Col>
        </Row>
      ))}
      <Button
        style={{ width: "100px" }}
        onClick={handleRun}
        type="warning"
        theme="solid"
        disabled={blocking}
        icon={<IconPlay />}
      >
        Run
      </Button>
      {result && <div style={{ margin: 0, whiteSpace: "pre-wrap" }}>{result}</div>}
    </Space>
  );
  return (
    <Popover trigger="click" content={renderContent} showArrow autoAdjustOverflow>
      <Button disabled={blocking && !running} icon={<IconChevronDown />} loading={running}>
        {name}
      </Button>
    </Popover>
  );
});
