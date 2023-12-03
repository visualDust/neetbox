import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import { LocaleProvider } from "@douyinfe/semi-ui";
import en_US from "@douyinfe/semi-ui/lib/es/locale/source/en_US";
import AppLayout from "./components/layout/AppLayout";
import LoginPage from "./pages/login";
import "./index.css";
import { consoleRoutes } from "./pages/console";
import { ThemeContextProvider } from "./components/themeSwitcher";
import { ServiceProvider } from "./services/serviceProvider";
import ConsoleLayout from "./components/layout/ConsoleLayout";

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        path: "",
        // element: <Home />,
        element: <ConsoleLayout />,
      },
      consoleRoutes(),
      {
        path: "/login",
        element: <LoginPage />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <LocaleProvider locale={en_US}>
      <ThemeContextProvider>
        <ServiceProvider>
          <RouterProvider router={router} />
        </ServiceProvider>
      </ThemeContextProvider>
    </LocaleProvider>
  </React.StrictMode>,
);
