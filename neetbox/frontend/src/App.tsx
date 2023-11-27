import { Layout, Button, Space, Typography } from "@douyinfe/semi-ui";
import { Link, Outlet } from "react-router-dom";
import SwitchColorMode from "./components/themeSwitcher";
import "./styles/global.css";
import FooterContent from "./components/Footer";

const { Header, Footer, Content } = Layout;

export default function AppLayout() {
  return (
    <Layout className="components-layout-demo" style={{ minHeight: "100vh" }}>
      <Header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "0 20px",
        }}
      >
        <Typography.Title>
          <Link to="/">NEET Center</Link>
        </Typography.Title>
        <div>
          <Space>
            <SwitchColorMode></SwitchColorMode>
            <Link to="/login">
              <Button>Login</Button>
            </Link>
          </Space>
        </div>
      </Header>
      <Layout>
        <Content style={{ flex: "1" }}>
          <Outlet />
        </Content>
      </Layout>
      <Footer children={<FooterContent />} />
    </Layout>
  );
}

export function Home() {
  return (
    <div>
      <Link to="/console">
        <Button>console</Button>
      </Link>
    </div>
  );
}
