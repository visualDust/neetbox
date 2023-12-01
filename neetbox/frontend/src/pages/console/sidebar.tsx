import { Nav } from "@douyinfe/semi-ui";
import React from "react";
import { IconHome, IconListView } from "@douyinfe/semi-icons";
import { Link, useLocation } from "react-router-dom";
import { useAPI } from "../../services/api";
import Loading from "../../components/loading";

export default function ConsoleNavBar() {
  const location = useLocation();
  const { data } = useAPI("/list", { refreshInterval: 5000 });
  return (
    <Nav
      renderWrapper={(args) => {
        if (args.props.itemKey === "loading") return <Loading height="60px" />;
        if (!(args.props.itemKey as string).startsWith("/")) return args.itemElement;
        return (
          <Link to={args.props.itemKey as string} style={{ textDecoration: "none" }}>
            {args.itemElement}
          </Link>
        );
      }}
      style={{ height: "100%", overflowY: "auto" }}
      items={[
        { itemKey: "/console/overview", text: "Overview", icon: <IconHome /> },
        {
          text: "Projects",
          icon: <IconListView />,
          itemKey: "projects",
          items: data
            ? data.map(({ id, config }) => ({
                text: config.value.name,
                itemKey: "/console/project/" + id,
              }))
            : [{ text: "", itemKey: "loading" }],
        },
      ]}
      defaultOpenKeys={["projects"]}
      selectedKeys={[location.pathname]}
      footer={{
        collapseButton: true,
      }}
    />
  );
}
