import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Space,
  Select,
  Tag,
  Button,
  Modal,
  Toast,
  SplitButtonGroup,
} from "@douyinfe/semi-ui";
import { IconArchive, IconArticle, IconDelete, IconEdit, IconInfoCircle } from "@douyinfe/semi-icons";
import { useNavigate } from "react-router-dom";
import Loading from "../common/loading";
import { useProjectRunStatus } from "../../hooks/useProject";
import { fetcher } from "../../services/api";
import { HyperParams } from "./hyperParams";
import { RunNotePopover, RunNoteEditorModal } from "./runNotes";
import { SingleRunEditor, MultiRunEditor } from "./runEdit";

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

  const [editingSingleRun, setEditingSingleRun] = useState<any>(null);
  const [editingAllRun, setEditingAllRun] = useState<boolean>(false);
  const [editingNote, setEditingNote] = useState<any>(null);
  const [runStatus, mutateRunStatus] = useProjectRunStatus(projectId, runId);

  return (
    <Space style={{ width: "700px" }}>
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
          style={{ backgroundColor: "var(--semi-color-nav-bg)" }}
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
                    setEditingSingleRun(item);
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
                <RunNotePopover
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
      <Button
        style={{ backgroundColor: "var(--semi-color-nav-bg)" }}
        icon={<IconArchive />}
        onClick={(e) => {
          e.stopPropagation();
          closeDropDown();
          setEditingAllRun(true);
        }}
      >Manage</Button>
      <HyperParams projectId={projectId} runId={runId}>
        <Button style={{ backgroundColor: "var(--semi-color-nav-bg)" }} icon={<IconInfoCircle />}>
          Params
        </Button>
      </HyperParams>
      <SplitButtonGroup>
        <RunNotePopover projectId={projectId} runId={runId}>
          <Button style={{ backgroundColor: "var(--semi-color-nav-bg)" }} icon={<IconArticle />}>
            Note
          </Button>
        </RunNotePopover>
        <Button
          style={{ backgroundColor: "var(--semi-color-nav-bg)" }}
          icon={<IconEdit />}
          onClick={(e) => {
            e.stopPropagation();
            setEditingNote(true);
            closeDropDown();
          }}
        />
      </SplitButtonGroup>
      {changing && <Loading height="30px" />}
      <SingleRunEditor
        data={editingSingleRun}
        onResult={useCallback(
          (edited) => {
            setEditingSingleRun(null);
            if (edited) {
              mutateRunIds();
            }
          },
          [mutateRunIds],
        )}
      />
      <MultiRunEditor
        visible={editingAllRun}
        data={items}
        onResult={useCallback(
          (edited) => {
            setEditingAllRun(false);
            if (edited) {
              mutateRunIds();
            }
          },
          [mutateRunIds],
        )}
      />
      <RunNoteEditorModal
        data={editingNote ? { projectId, runId, notes: runStatus?.metadata.notes } : null}
        onResult={(edited) => {
          setEditingNote(false);
          if (edited) {
            mutateRunStatus();
          }
        }}
      />
    </Space>
  );
});

