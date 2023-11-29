import { Nav } from "@douyinfe/semi-ui";
import React from "react";
import { IconStar, IconSetting } from "@douyinfe/semi-icons";
import { Link, useLocation } from "react-router-dom";
import { useAPI } from "../../services/api";

export default function ConsoleNavBar() {
  const location = useLocation();
  const { isLoading, data, error } = useAPI("/list", { refreshInterval: 5000 });
  return (
    <Nav
      renderWrapper={(args) => {
        if (!(args.props.itemKey as string).startsWith("/")) return args.itemElement;
        return (
          <Link to={args.props.itemKey as string} style={{ textDecoration: "none" }}>
            {args.itemElement}
          </Link>
        );
      }}
      bodyStyle={{ height: 320 }}
      items={[
        { itemKey: "/console/overview", text: "Overview", icon: <IconStar /> },
        {
          text: "Projects",
          icon: <IconSetting />,
          itemKey: "projects",
          items: data?.names.map((name: string) => ({
            text: name,
            itemKey: "/console/project/" + name,
          })) ?? ["(loading...)"],
        },
      ]}
      defaultOpenKeys={["projects"]}
      selectedKeys={[location.pathname]}
      onClick={(data) => console.log("trigger onClick: ", data)}
      footer={{
        collapseButton: true,
      }}
    />
  );
}
