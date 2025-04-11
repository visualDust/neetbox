import { memo, useEffect, useRef, useState } from "react";
import { Button, Popover, Space, Typography, MarkdownRender, Modal } from "@douyinfe/semi-ui";
import { IconArticle } from "@douyinfe/semi-icons";
import { useCurrentProject, useProjectRunStatus } from "../../hooks/useProject";
import Loading from "../common/loading";
import MDEditor from "@uiw/react-md-editor";
import "katex/dist/katex.css";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
import remarkGfm from "remark-gfm";
import { fetcher } from "../../services/api";
import { ErrorBoundary } from "../common/errorBoundary";

export const RunNotePopover = memo(
  ({ projectId, runId, trigger = "click", position, allowEdit = true, children = <IconArticle /> }: any) => {
    const [runStatus, mutateRunStatus] = useProjectRunStatus(projectId, runId);
    const value = runStatus?.metadata?.notes;
    const [editing, realSetEditing] = useState(false);
    const [popoverVisible, setPopoverVisible] = useState(false);
    const setEditing = (value) => {
      realSetEditing(value);
      if (value) {
        setPopoverVisible(false);
      }
    };

    return (
      <>
        <Popover
          showArrow
          trigger={trigger}
          position={position}
          content={<RunNoteContent {...{ runStatus, value, setEditing, allowEdit }} />}
          visible={popoverVisible}
          onVisibleChange={setPopoverVisible}
        >
          {children}
        </Popover>
        <RunNoteEditorModal
          data={editing ? { projectId, runId, notes: value } : null}
          onResult={(edited) => {
            setEditing(false);
            if (edited) {
              mutateRunStatus();
            }
          }}
        />
      </>
    );
  },
);

const RunNoteContent = memo(({ runStatus, value, setEditing, allowEdit }: any) => {
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
          <ErrorBoundary renderError={(error) => `Markdown Error: ${error.message}`}>
            <MarkdownRender
              format="mdx"
              raw={value}
              remarkPlugins={[remarkMath, remarkGfm]}
              rehypePlugins={[rehypeKatex]}
              style={{ maxWidth: "calc(min(960px, 100vw - 50px))", maxHeight: "80vh", overflow: "auto" }}
            />
          </ErrorBoundary>
          {allowEdit && (
            <Button
              icon={<IconArticle />}
              type="tertiary"
              onClick={(e) => {
                setEditing(true);
              }}
            >
              Edit Note
            </Button>
          )}
        </>
      )}
    </Space>
  );
});

export const RunNoteEditorModal = memo((props: { data: any; onResult: (edited: boolean) => void }) => {
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
      title={
        <Space>
          <IconArticle />
          Project
          <Typography.Text type="tertiary">{data.projectId}</Typography.Text>
          Run
          <Typography.Text type="tertiary">{data.runId}</Typography.Text>
        </Space>
      }
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
      size="large"
      centered
    >
      <MDEditor
        value={data.notes}
        onChange={(v) => {
          setData({ ...data, notes: v });
        }}
        textareaProps={{
          placeholder: "Please enter Markdown text...",
        }}
        height="480px"
        data-color-mode={document.body.getAttribute("theme-mode") === "dark" ? "dark" : "light"}
        previewOptions={{
          rehypePlugins: [rehypeKatex],
          remarkPlugins: [remarkMath, remarkGfm],
        }}
      />
    </Modal>
  );
});
