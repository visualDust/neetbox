import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Space, Select, Tag, Button, Modal, Form } from "@douyinfe/semi-ui";
import { IconDelete, IconEdit } from "@douyinfe/semi-icons";
import Loading from "../../loading";
import { useCurrentProject } from "../../../hooks/useProject";

export const RunSelect = memo(({ runIds, setRunId }: { runIds; setRunId }) => {
  const { runId, isOnlineRun, projectOnline } = useCurrentProject();

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
          {items.map((x, i) => (
            <Select.Option style={{ gap: "5px" }} key={x.id} value={x.id}>
              {x.timestamp}
              <span style={{ fontFamily: "monospace", fontSize: 12 }}>({x.id})</span>
              <Button
                type="secondary"
                icon={<IconEdit />}
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  closeDropDown();
                  setEditing(x);
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
                      content: `Deleting run ${x.timestamp} (${x.id})`,
                      centered: true,
                      onOk: async () => {
                        await new Promise((r) => setTimeout(r, 1000));
                      },
                    });
                  }}
                />
              )}
              {i == 0 && (projectOnline ? <Tag color="green">Online</Tag> : <Tag color="red">Offline</Tag>)}
            </Select.Option>
          ))}
        </Select>
      ) : (
        <Loading height="30px" />
      )}
      {changing && <Loading height="30px" />}
      <RunEditor
        data={editing}
        onResult={useCallback(() => {
          setEditing(null);
        }, [])}
      />
    </Space>
  );
});

const RunEditor = memo((props: { data: any; onResult: (data: any) => void }) => {
  const [data, setData] = useState<any>({});
  const [visible, setVisible] = useState(false);
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
      onCancel={() => props.onResult(null)}
      onOk={async () => {
        await new Promise((r) => setTimeout(r, 1000));
        props.onResult(data);
      }}
      okText="Submit"
      centered
    >
      <Form initValues={data}>
        <Form.Input field="id" label="ID" disabled></Form.Input>
        <Form.Input field="name" label="Name"></Form.Input>
      </Form>
    </Modal>
  );
});
