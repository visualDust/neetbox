import { Layout } from "@douyinfe/semi-ui";
import { Outlet } from "react-router-dom";
import ConsoleNavBar from "../../pages/console/sidebar";
import AppFooter from "./AppFooter";

export default function ConsoleLayout() {
  const { Sider, Content } = Layout;
  return (
    <Layout style={{ height: "100%" }}>
      <Sider style={{ background: "var(--semi-color-fill-2)" }}>
        <ConsoleNavBar />
      </Sider>
      <Content style={{ display: "flex", flexDirection: "column", height: "100%", overflow: "auto" }}>
        <Outlet />
        <AppFooter />
      </Content>
    </Layout>
  );
}
