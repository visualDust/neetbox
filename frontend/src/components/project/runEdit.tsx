import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
    Button,
    Modal,
    Form,
    Table,
    Spin,
    Space,
    Toast,
    Typography,
    SplitButtonGroup,
} from "@douyinfe/semi-ui";
import { IconArticle, IconCopy, IconDelete, IconEdit, IconInfoCircle } from "@douyinfe/semi-icons";
import { FormApi } from "@douyinfe/semi-ui/lib/es/form";
import { useCurrentProject, useProjectRunStatus } from "../../hooks/useProject";
import { fetcher } from "../../services/api";
import { HyperParams } from "./hyperParams";
import { RunNotePopover } from "./runNotes";

export const SingleRunEditor = memo((props: { data: any; onResult: (edited: boolean) => void }) => {
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

export const MultiRunEditor = memo((props: { visible: boolean; data: any[]; onResult: (updated: boolean) => void }) => {
    const { visible, onResult } = props;
    const { projectId } = useCurrentProject();
    const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
    const [loading, setLoading] = useState(false);
    const runs = props.data ?? [];

    const handleDelete = useCallback(() => {
        Modal.confirm({
            title: "Confirm Deletion",
            content: `Are you sure you want to delete ${selectedKeys.length} selected run(s)?`,
            onOk: async () => {
                setLoading(true);
                try {
                    for (const key of selectedKeys) {
                        await fetcher(`/project/${projectId}/run/${key}`, {
                            method: "DELETE",
                        });
                    }
                    Toast.success("Selected runs deleted successfully.");
                    setSelectedKeys([]);
                    onResult(true);
                } catch (e) {
                    Toast.error("Failed to delete some runs: " + e);
                } finally {
                    setLoading(false);
                }
            },
        });
    }, [selectedKeys, projectId, onResult]);

    const columns = useMemo(() => [
        {
            title: "Name",
            dataIndex: "metadata",
            render: (metadata: { name: string }, record: any) => (
                <>
                    <Typography.Text>{metadata.name ? metadata.name : "Name not set"}</Typography.Text>
                    <br />
                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                        {record.runId}
                    </Typography.Text>
                </>
            ),
        },
        {
            title: "Created At",
            dataIndex: "timestamp",
            render: (text: string) => {
                const date = new Date(text);
                return date.toLocaleDateString() + " " + date.toLocaleTimeString();
            }
        },
        {
            title: "Misc",
            dataIndex: "",
            render: (record: any) => (
                <>
                    <SplitButtonGroup>
                        <HyperParams projectId={projectId} runId={record.runId}>
                            <Button icon={<IconInfoCircle />}>
                                Params
                            </Button>
                        </HyperParams>
                        <RunNotePopover projectId={projectId} runId={record.runId}>
                            <Button icon={<IconArticle />}>
                                Note
                            </Button>
                        </RunNotePopover>
                    </SplitButtonGroup>
                </>
            )
        }

    ], []);


    const colorizeRow = (record, index) => {
        if (index % 2 === 0) {
            return {
                style: {
                    background: "var(--semi-color-fill-0)",
                },
            };
        } else {
            return {};
        }
    };

    return (
        <Modal
            title="Batch Manage Runs"
            visible={visible}
            onCancel={() => props.onResult(false)}
            footer={null}
            centered
            width={800}
        >
            <Spin spinning={loading}>
                <Space style={{ marginBottom: 16 }}>

                    <Button
                        icon={<IconDelete />}
                        type="danger"
                        disabled={selectedKeys.length === 0}
                        onClick={handleDelete}
                    >
                        Delete Selected
                    </Button>
                </Space>
                <Table
                    rowKey="runId"
                    columns={columns}
                    dataSource={runs.filter((run) => run.online === false)}
                    onRow={colorizeRow}
                    rowSelection={{
                        selectedRowKeys: selectedKeys as (string | number)[],
                        onChange: (selectedRowKeys) => setSelectedKeys(selectedRowKeys || []),
                    }}
                />
                <div style={{ marginBottom: 20 }}>
                    <Typography.Text type="secondary">
                        Note: Only runs that are not currently running can be deleted.

                    </Typography.Text>
                    <br />
                    <Typography.Text type="danger" strong={true}>
                        Please be careful when deleting runs. Deleted runs cannot be recovered.
                    </Typography.Text>
                </div>
            </Spin>
        </Modal>
    );
});