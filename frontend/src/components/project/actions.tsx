import { Button, Checkbox, Col, Input, Popover, Row, Space, Typography } from "@douyinfe/semi-ui";
import { memo, useState } from "react";
import { IconChevronDown, IconPlay } from "@douyinfe/semi-icons";
import { getProject } from "../../services/projects";
import { useMemoJSON } from "../../hooks/useMemoJSON";
import { ActionInfo } from "../../services/types";
import { useCurrentProject, useProjectRunStatus } from "../../hooks/useProject";
import Loading from "../common/loading";

export function Actions() {
  const { projectId, runId } = useCurrentProject();
  const [status] = useProjectRunStatus(projectId, runId);
  const actions = status?.action as ActionInfo;
  const actionListMemo = Object.entries(useMemoJSON(actions ?? {}));
  const [blocking, setBlocking] = useState(false);
  return !status ? (
    <Loading size="large" />
  ) : !status.action ? (
    <Typography.Text>
      No actions (
      <a target="_blank" href="https://neetbox.550w.host/docs/howto/PythonAPIs/create-actions/">
        docs
      </a>
      )
    </Typography.Text>
  ) : (
    <Space style={{ marginBottom: "20px" }} spacing="medium" wrap>
      {actionListMemo.map(([actionName, actionOptions]) => (
        <ActionItem
          key={actionName}
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
  actionOptions: ActionInfo[string];
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
  const { projectId, runId, isOnlineRun } = useCurrentProject()!;
  const handleRun = () => {
    if (options.blocking) setBlocking(true);
    setCurrentBlocking(true);
    getProject(projectId).sendAction(runId!, name, args, ({ error: err, result: res }) => {
      if (options.blocking) setBlocking(false);
      setCurrentBlocking(false);
      setResult(err ? `error:\n${err}` : `result:\n${JSON.stringify(res)}`);
    });
  };
  const renderContent = () => (
    <Space vertical spacing={"tight"} style={{ minWidth: "200px", maxWidth: "500px" }}>
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
          <Col span={13}>
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
          <Col span={4}>
            <Typography.Text ellipsis={{ showTooltip: true }}>({argType})</Typography.Text>
          </Col>
        </Row>
      ))}
      <Button
        style={{ width: "100px" }}
        onClick={handleRun}
        type="warning"
        theme="solid"
        disabled={blocking || !isOnlineRun}
        icon={<IconPlay />}
      >
        Run
      </Button>
      {!isOnlineRun && (
        <Typography.Text type="tertiary">(can not run in offline / history view)</Typography.Text>
      )}
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
