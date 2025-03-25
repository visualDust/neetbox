import { memo, useEffect, useRef, useState } from "react";
import { Button, Popover, Space, Typography, MarkdownRender, Modal } from "@douyinfe/semi-ui";
import { IconArticle } from "@douyinfe/semi-icons";
import { useCurrentProject, useProjectRunStatus } from "../../hooks/useProject";
import Loading from "../common/loading";
import MDEditor from "@uiw/react-md-editor";
import { fetcher } from "../../services/api";

export const RunNote = memo(
  ({ projectId, runId, trigger = "click", position, allowEdit = true, children = <IconArticle /> }: any) => {
    return (
      <Popover
        showArrow
        trigger={trigger}
        position={position}
        content={<RunNoteContent projectId={projectId} runId={runId} allowEdit={allowEdit} />}
      >
        {children}
      </Popover>
    );
  },
);

const RunNoteContent = memo(({ projectId, runId, allowEdit }: any) => {
  const runStatus = useProjectRunStatus(projectId, runId);
  const value = runStatus?.metadata.notes;
  const [editing, setEditing] = useState(false);
  return (
    <Space vertical>
      {!runStatus ? (
        <Loading />
      ) : value == null ? (
        allowEdit ? (
          <Button
            icon={<IconArticle />}
            type="tertiary"
            onClick={(e) => {
              e.stopPropagation();
              setEditing(true);
            }}
          >
            Add Note
          </Button>
        ) : (
          <Typography.Text type="tertiary">N/A</Typography.Text>
        )
      ) : (
        <>
          <MarkdownRender raw={value} />
          {allowEdit && (
            <Button
              icon={<IconArticle />}
              type="tertiary"
              onClick={(e) => {
                e.stopPropagation();
                setEditing(true);
              }}
            >
              Edit Note
            </Button>
          )}
        </>
      )}
      <RunNoteEditor
        data={editing ? { runId, notes: value } : null}
        onResult={(edited) => {
          setEditing(false);
          if (edited) {
            // todo trigger a refresh
          }
        }}
      />
    </Space>
  );
});

const RunNoteEditor = memo((props: { data: any; onResult: (edited: boolean) => void }) => {
  const { projectId } = useCurrentProject();
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
      title={`Run Note`}
      visible={visible}
      onCancel={() => props.onResult(false)}
      onOk={async () => {
        await fetcher(`/project/${projectId}/run/${data.runId}`, {
          method: "PUT",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            notes: data.notes,
          }),
        });
        props.onResult(true);
      }}
      okText="Submit"
      maskClosable={false}
      fullScreen={true}
      centered
    >
      <MDEditor
        value={data.notes}
        onChange={(v) => {
          setData({ ...data, notes: v });
        }}
        height="60%"
      />
    </Modal>
  );
});
