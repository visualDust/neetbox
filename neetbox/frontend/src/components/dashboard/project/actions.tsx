import {
  Button,
  Col,
  Input,
  Popover,
  Row,
  Space,
  Typography,
} from "@douyinfe/semi-ui";
import { ProjectStatus } from "../../../services/projects";

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
  actionOptions,
}: {
  name: string;
  actionOptions: ProjectStatus["__action"]["value"][string];
}) {
  const renderContent = () => (
    <div style={{ padding: "10px" }}>
      <Space vertical spacing={"tight"}>
        <Typography.Title heading={5}>"{name}"</Typography.Title>
        {actionOptions.args.map((argName) => (
          <Row align="middle">
            <Col span={4}>
              <Typography.Text>{argName}</Typography.Text>
            </Col>
            <Col span={20}>
              <Input size="small" />
            </Col>
          </Row>
        ))}
        <Button style={{ width: "100px" }}>Run</Button>
      </Space>
    </div>
  );
  return (
    <Popover trigger="click" content={renderContent()}>
      <Button>{name}</Button>
    </Popover>
  );
}
