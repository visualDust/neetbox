import { Nav } from "@douyinfe/semi-ui";
import React from "react";
import { IconStar, IconSetting } from "@douyinfe/semi-icons";
import { useAPI } from "../../hooks/useAPI";
import { Link } from "react-router-dom";

export default function ConsoleNavBar() {
  const { isLoading, data, error } = useAPI("/status/list");
  return (
    <Nav
      renderWrapper={(args) => {
        if (!args.props.itemKey.startsWith("/")) return args.itemElement;
        return (
          <Link
            to={args.props.itemKey as string}
            style={{ textDecoration: "none" }}
          >
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
      onClick={(data) => console.log("trigger onClick: ", data)}
      footer={{
        collapseButton: true,
      }}
    />
  );
}
