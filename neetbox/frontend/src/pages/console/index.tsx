import { Component } from "react";
import { Layout } from "@douyinfe/semi-ui";
import { Outlet, RouteObject } from "react-router-dom";
import ConsoleNavBar from "./sidebar";
import Dashboard from "./proejctDashboard";
import Overview from "./overview";

export function consoleRoutes(): RouteObject {
  return {
    path: "console",
    element: <Console />,
    children: [
      { path: "project/:projectName", element: <Dashboard />, errorElement: <div>Error</div> },
      { path: "overview", element: <Overview /> },
    ],
  };
}

export default class Console extends Component {
  render() {
    const { Sider, Content } = Layout;
    return (
      <Layout>
        <Sider style={{ background: "var(--semi-color-fill-2)" }}>
          <ConsoleNavBar></ConsoleNavBar>
        </Sider>
        <Content>
          <Outlet />
        </Content>
      </Layout>
    );
  }
}
