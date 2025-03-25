import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Space, Select, Tag, Button, Modal, Form, Toast } from "@douyinfe/semi-ui";
import { IconArticle, IconCopy, IconDelete, IconEdit, IconInfoCircle } from "@douyinfe/semi-icons";
import { FormApi } from "@douyinfe/semi-ui/lib/es/form";
import { useNavigate } from "react-router-dom";
import Loading from "../common/loading";
import { useCurrentProject } from "../../hooks/useProject";
import { fetcher } from "../../services/api";
import { HyperParams } from "./hyperParams";
import { RunNote } from "./runNotes";

export const RunSelect = memo((props: any) => {
  const { setRunId, runIds, mutateRunIds, projectId, runId, isOnlineRun } = props;
  const navigate = useNavigate();
  const items = useMemo(
    () =>
      [...(runIds ?? [])]
        .reverse()
        .map((x) => ({ ...x, timestamp: x.timestamp.slice(0, 19).replace("T", " ") })),
    [runIds],
  );

  const [changing, setChanging] = useState(false);
  const handleChangeRun = (runId: string) => {
    setChanging(true);
    setTimeout(() => {
      setRunId(runId);
    }, 10);
  };
  useEffect(() => {
    setChanging(false);
  }, [runId]);

  const selectRef = useRef<any>();
  const closeDropDown = () => selectRef.current.close();

  const [editing, setEditing] = useState<any>(null);

  return (
    <Space style={{ width: "500px" }}>
      {runIds ? (
        <Select
          ref={selectRef}
          value={runId}
          onChange={(x) => handleChangeRun(x as string)}
          maxHeight={"70vh"}
          renderSelectedItem={(p) => (
            <>
              {isOnlineRun ? (
                <Tag color="green">Online</Tag>
              ) : runId != items?.[0].runId ? (
                <Tag color="orange">History</Tag>
              ) : (
                <Tag color="red">Offline</Tag>
              )}
              {items.find((x) => x.runId == p.value)?.timestamp}
            </>
          )}
        >
          {items.map((item, i) => {
            return (
              <Select.Option
                style={{ gap: "5px" }}
                // workaround for semi-design select: won't update label unless key changed
                // https://github.com/DouyinFE/semi-design/blob/c7982af07ad92e6cafe72d96604ed63a8ca595d6/packages/semi-ui/select/index.tsx#L640
                key={item.runId + "-" + item.metadata?.name + "-" + item.online}
                value={item.runId}
              >
                <span style={{ fontFamily: "monospace", fontSize: 12 }}>{item.timestamp}</span>
                <span style={{ fontFamily: "monospace", fontSize: 12 }}>
                  ({item.metadata?.name ?? item.runId})
                </span>
                <span style={{ flex: 1 }}></span>
                <Button
                  type="secondary"
                  icon={<IconEdit />}
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    closeDropDown();
                    setEditing(item);
                  }}
                />
                {!item.online && (
                  <Button
                    type="danger"
                    icon={<IconDelete />}
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      closeDropDown();
                      Modal.error({
                        title: "Are you sure?",
                        content: `Deleting run ${item.timestamp} (${item.runId})`,
                        centered: true,
                        onOk: async () => {
                          if (item.runId === runId) {
                            const existedId = runIds.find((x) => x.runId !== runId);
                            if (existedId) {
                              setRunId(existedId);
                            } else {
                              navigate("/");
                            }
                          }
                          await fetcher(`/project/${projectId}/run/${item.runId}`, { method: "DELETE" });
                          mutateRunIds();
                          Toast.success({
                            content: `Deleted ${item.timestamp}`,
                          });
                        },
                      });
                    }}
                  />
                )}
                {item.online ? <Tag color="green">Online</Tag> : <Tag color="red">Offline</Tag>}
                <HyperParams projectId={projectId} runId={item.runId} trigger="hover" position="leftTop">
                  <Button type="tertiary" icon={<IconInfoCircle />} size="small" />
                </HyperParams>
                <RunNote
                  projectId={projectId}
                  runId={item.runId}
                  trigger="hover"
                  position="rightTop"
                  allowEdit={false}
                />
              </Select.Option>
            );
          })}
        </Select>
      ) : (
        <Loading height="30px" />
      )}
      <HyperParams projectId={projectId} runId={runId}>
        <Button type="tertiary" icon={<IconInfoCircle />}>
          Params
        </Button>
      </HyperParams>
      <RunNote projectId={projectId} runId={runId}>
        <Button icon={<IconArticle />}>Note</Button>
      </RunNote>
      {changing && <Loading height="30px" />}
      <RunEditor
        data={editing}
        onResult={useCallback(
          (edited) => {
            setEditing(null);
            if (edited) {
              mutateRunIds();
            }
          },
          [mutateRunIds],
        )}
      />
    </Space>
  );
});

const RunEditor = memo((props: { data: any; onResult: (edited: boolean) => void }) => {
  const { projectId } = useCurrentProject();
  const [data, setData] = useState<any>({});
  const [visible, setVisible] = useState(false);
  const formRef = useRef<{ formApi: FormApi }>(null!);
  useEffect(() => {
    if (props.data) {
      setData(props.data);
    }
    setVisible(Boolean(props.data));
  }, [props.data]);
  return (
    <Modal
      title={`Run Info`}
      visible={visible}
      onCancel={() => props.onResult(false)}
      onOk={async () => {
        const values = formRef.current.formApi.getValues();
        await fetcher(`/project/${projectId}/run/${data.runId}`, {
          method: "PUT",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            name: values.metadata.name,
          }),
        });
        props.onResult(true);
      }}
      okText="Submit"
      centered
    >
      <Form initValues={data} ref={formRef as any}>
        <Form.Input
          field="runId"
          label="ID"
          extraText={
            <Button icon={<IconCopy />} onClick={() => navigator.clipboard.writeText(data.runId)}>
              Copy ID
            </Button>
          }
          readOnly={true}
          disabled
        ></Form.Input>
        <Form.Input field="metadata.name" label="Name"></Form.Input>
      </Form>
    </Modal>
  );
});
