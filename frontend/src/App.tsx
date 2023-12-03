import { Layout } from "@douyinfe/semi-ui";
import { Outlet } from "react-router-dom";
import { useReportGlobalError } from "./hooks/useReportError";
import AppHeader from "./components/layout/AppHeader";
import "./styles/global.css";

export default function App() {
  useReportGlobalError();
  return (
    <Layout style={{ height: "100vh" }}>
      <AppHeader />
      <Layout.Content style={{ flex: "1", overflow: "hidden" }}>
        <Outlet />
      </Layout.Content>
    </Layout>
  );
}
