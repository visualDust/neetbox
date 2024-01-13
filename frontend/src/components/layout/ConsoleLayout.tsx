import { Layout } from "@douyinfe/semi-ui";
import { Outlet } from "react-router-dom";
import ConsoleNavBar from "../../pages/console/sidebar";
import { ErrorBoundary } from "../common/errorBoundary";
import AppFooter from "./AppFooter";

export default function ConsoleLayout() {
  const { Sider, Content } = Layout;
  return (
    <Layout style={{ height: "100%" }}>
      <ErrorBoundary>
        <Sider style={{ background: "var(--semi-color-fill-2)" }}>
          <ConsoleNavBar />
        </Sider>
      </ErrorBoundary>
      <Content
        style={{
          display: "flex",
          flexDirection: "column",
          height: "100%",
          overflowY: "auto",
          overflowX: "hidden",
        }}
      >
        <Outlet />
        <AppFooter />
      </Content>
    </Layout>
  );
}
