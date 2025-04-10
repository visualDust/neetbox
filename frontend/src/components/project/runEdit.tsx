import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
    Button,
    Modal,
    Form,
    Table,
    Spin,
    Checkbox,
    Space,
    Toast,
} from "@douyinfe/semi-ui";
import { IconArticle, IconCopy, IconDelete, IconEdit, IconInfoCircle } from "@douyinfe/semi-icons";
import { FormApi } from "@douyinfe/semi-ui/lib/es/form";
import { useCurrentProject, useProjectRunStatus } from "../../hooks/useProject";
import { fetcher } from "../../services/api";

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

export const MultiRunEditor = memo((props: { data: any[]; onResult: (updated: boolean) => void }) => {
    const { projectId } = useCurrentProject();
    const [visible, setVisible] = useState(false);
    const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
    const [loading, setLoading] = useState(false);
    const [runs, setRuns] = useState<any[]>([]);

    useEffect(() => {
        if (props.data && props.data.length > 0) {
            setRuns(props.data);
            setVisible(true);
        }
    }, [props.data]);

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
                    setRuns(prev => prev.filter(item => !selectedKeys.includes(item.runId)));
                    setSelectedKeys([]);
                    props.onResult(true);
                } catch (e) {
                    Toast.error("Failed to delete some runs: " + e);
                } finally {
                    setLoading(false);
                }
            },
        });
    }, [selectedKeys, projectId, props]);

    const columns = useMemo(() => [
        {
            title: "ID",
            dataIndex: "runId",
            render: (text: string) => <span style={{ wordBreak: "break-all" }}>{text}</span>,
        },
        {
            title: "Name",
            dataIndex: "metadata",
            render: (metadata: { name: string }) => metadata?.name,
        },
    ], []);

    return (
        <Modal
            title="Manage Runs"
            visible={visible}
            onCancel={() => setVisible(false)}
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
                    dataSource={runs}
                    pagination={false}
                    rowSelection={{
                        selectedRowKeys: selectedKeys as (string | number)[],
                        onChange: (selectedRowKeys) => setSelectedKeys(selectedRowKeys || []),
                    }}
                />
            </Spin>
        </Modal>
    );
});