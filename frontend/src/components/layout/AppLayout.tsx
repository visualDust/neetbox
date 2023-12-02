import { Layout } from "@douyinfe/semi-ui";
import { Outlet } from "react-router-dom";
import AppHeader from "./AppHeader";
import "../../styles/global.css";

export default function AppLayout() {
  return (
    <Layout style={{ height: "100vh" }}>
      <AppHeader />
      <Layout.Content style={{ flex: "1", overflow: "hidden" }}>
        <Outlet />
      </Layout.Content>
    </Layout>
  );
}
