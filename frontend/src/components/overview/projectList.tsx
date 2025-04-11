import React, { useEffect, useState, useRef } from "react";
import { Table, Input, Space, Tag, Toast, Button, ButtonGroup } from "@douyinfe/semi-ui";
import { IconCopy, IconGlobeStroke, IconCloud, IconMore } from "@douyinfe/semi-icons";
import { useAPI } from "../../services/api";
import { useNavigate } from "react-router-dom";
import * as dateFns from "date-fns";

const copyToClipboard = (value: string) => {
  navigator.clipboard
    .writeText(value)
    .then(() => {
      Toast.info("Copied to clipboard");
    })
    .catch(() => {
      Toast.error("Failed to copy");
    });
};

export default function ProjectList() {
  const { data = [] } = useAPI("/project/list", { refreshInterval: 5000 });
  const [filteredValue, setFilteredValue] = useState<string[]>([]);
  const navigate = useNavigate();
  const compositionRef = useRef({ isComposition: false });

  const handleChange = (value: string) => {
    if (!compositionRef.current.isComposition) {
      setFilteredValue(value ? [value] : []);
    }
  };

  const handleCompositionStart = () => {
    compositionRef.current.isComposition = true;
  };

  const handleCompositionEnd = (event: React.CompositionEvent<HTMLInputElement>) => {
    compositionRef.current.isComposition = false;
    const value = event.currentTarget.value;
    setFilteredValue(value ? [value] : []);
  };

  const columns = [
    {
      title: (
        <Space>
          Name
          <Input
            placeholder="Search"
            style={{ width: 200 }}
            onCompositionStart={handleCompositionStart}
            onCompositionEnd={handleCompositionEnd}
            onChange={handleChange}
            showClear
          />
        </Space>
      ),
      dataIndex: "name",
      filteredValue,
      onFilter: (value: string, record: any) => record.name.includes(value),
      render: (text: string, record: any) => (
        <ButtonGroup>
          <Button onClick={() => navigate(`/project/${record.projectId}`)}>{text}</Button>
          <Button
            icon={<IconCopy />}
            onClick={() => {
              copyToClipboard(record.projectId);
            }}
          >
            ID
          </Button>
        </ButtonGroup>
      ),
    },
    {
      title: "Online Status",
      dataIndex: "online",
      align: "center" as "center",
      render: (online: boolean, record: any) => (
        <Space>
          <Tag color={online ? "green" : "red"} prefixIcon={online ? <IconGlobeStroke /> : <IconCloud />}>
            {online ? "Online" : "Offline"}
          </Tag>
          <Tag>{record.runids.length} runs</Tag>
        </Space>
      ),
    },
    {
      title: "Last Launch",
      dataIndex: "time",
      render: (time: string) => dateFns.format(new Date(time), "yyyy-MM-dd HH:mm:ss"),
      sorter: (a: any, b: any) => new Date(a.time).getTime() - new Date(b.time).getTime(),
    },
    {
      title: "Log Size",
      dataIndex: "storage",
      render: (value: number) => `${(value / 1e6).toFixed(2)} MB`,
      sorter: (a: any, b: any) => a.storage - b.storage,
    },
  ];

  // Format data
  const dataSource = data.map((proj: any) => {
    const latestTime =
      proj.runids.length > 0
        ? proj.runids
            .map((r: any) => r.timestamp)
            .sort()
            .reverse()[0]
        : "-";

    return {
      ...proj,
      key: proj.projectId,
      time: latestTime,
    };
  });

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

  return <Table columns={columns} dataSource={dataSource} onRow={colorizeRow} />;
}
