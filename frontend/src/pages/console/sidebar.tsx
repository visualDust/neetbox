import { Nav, Space, Tag, Typography } from "@douyinfe/semi-ui";
import { IconHome, IconListView } from "@douyinfe/semi-icons";
import { useLocation, useNavigate } from "react-router-dom";
import { useAPI } from "../../services/api";
import Loading from "../../components/loading";

export default function ConsoleNavBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { data } = useAPI("/list", { refreshInterval: 5000 });
  return (
    <Nav
      renderWrapper={(args) => {
        if (args.props.itemKey === "loading") return <Loading height="60px" size="large" />;
        return args.itemElement;
      }}
      style={{ height: "100%", overflowY: "auto" }}
      items={[
        { itemKey: "/", text: "Overview", icon: <IconHome /> },
        {
          text: "Projects",
          icon: <IconListView />,
          itemKey: "projects",
          items: data
            ? data.map(({ projectid: id, name, online }) => ({
                text: (
                  <Space style={{ width: "100%" }}>
                    <Typography.Text
                      type={online ? "primary" : "tertiary"}
                      style={{ flex: "1 1 50%" }}
                      ellipsis={{ showTooltip: true }}
                    >
                      {name}
                    </Typography.Text>
                    {online && (
                      <Tag style={{ marginLeft: "10px" }} color="green">
                        Online
                      </Tag>
                    )}
                  </Space>
                ),
                itemKey: "/project/" + id,
              }))
            : [{ text: "", itemKey: "loading" }],
        },
      ]}
      onClick={(data) => {
        if ((data.itemKey as string).startsWith("/")) {
          navigate(data.itemKey as string);
        }
      }}
      defaultOpenKeys={["projects"]}
      selectedKeys={[location.pathname]}
      footer={{
        collapseButton: true,
      }}
    />
  );
}
