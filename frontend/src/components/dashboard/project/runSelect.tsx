import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Space, Select, Tag, Button, Modal, Form, Toast } from "@douyinfe/semi-ui";
import { IconDelete, IconEdit } from "@douyinfe/semi-icons";
import { FormApi } from "@douyinfe/semi-ui/lib/es/form";
import Loading from "../../loading";
import { useCurrentProject, useProjectRunIds } from "../../../hooks/useProject";
import { fetcher } from "../../../services/api";

export const RunSelect = memo((props: any) => {
  const { setRunId, runIds, mutateRunIds, projectId, runId, isOnlineRun, projectOnline } = props;
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
    <Space style={{ width: "320px" }}>
      Run:
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
              ) : runId != items[0].id ? (
                <Tag color="orange">History</Tag>
              ) : (
                <Tag color="red">Offline</Tag>
              )}
              {items.find((x) => x.id == p.value).timestamp}
            </>
          )}
        >
          {items.map((item, i) => {
            return (
              <Select.Option
                style={{ gap: "5px" }}
                // workaround for semi-design select: won't update label unless key changed
                // https://github.com/DouyinFE/semi-design/blob/c7982af07ad92e6cafe72d96604ed63a8ca595d6/packages/semi-ui/select/index.tsx#L640
                key={item.id + "-" + item.metadata?.name + "-" + (i == 0 ? projectOnline : "")}
                value={item.id}
              >
                <span style={{ fontFamily: "monospace", fontSize: 12 }}>{item.timestamp}</span>
                <span style={{ fontFamily: "monospace", fontSize: 12 }}>
                  ({item.metadata?.name ?? item.id})
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
                {!(i == 0 && projectOnline) && (
                  <Button
                    type="danger"
                    icon={<IconDelete />}
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      closeDropDown();
                      Modal.error({
                        title: "Are you sure?",
                        content: `Deleting run ${item.timestamp} (${item.id})`,
                        centered: true,
                        onOk: async () => {
                          // await new Promise((r) => setTimeout(r, 1000));
                          await fetcher(`/project/${projectId}/run/${item.id}`, { method: "DELETE" });
                          mutateRunIds();
                          Toast.success({
                            content: `Deleted ${item.timestamp}`,
                          });
                        },
                      });
                    }}
                  />
                )}
                {i == 0 && (projectOnline ? <Tag color="green">Online</Tag> : <Tag color="red">Offline</Tag>)}
              </Select.Option>
            );
          })}
        </Select>
      ) : (
        <Loading height="30px" />
      )}
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
        await fetcher(`/project/${projectId}/run/${data.id}`, {
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
        <Form.Input field="id" label="ID" disabled></Form.Input>
        <Form.Input field="metadata.name" label="Name"></Form.Input>
      </Form>
    </Modal>
  );
});
