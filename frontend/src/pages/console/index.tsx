import { RouteObject } from "react-router-dom";
import ConsoleLayout from "../../components/layout/ConsoleLayout";
import { RouteError } from "../../components/errorBoundary";
import Dashboard from "./projectDashboard";
import Overview from "./overview";

export function consoleRoutes(): RouteObject {
  return {
    path: "console",
    element: <ConsoleLayout />,
    children: [
      {
        path: "project/:projectId",
        element: <Dashboard />,
        errorElement: <RouteError />,
      },
      { path: "overview", element: <Overview /> },
    ],
  };
}
