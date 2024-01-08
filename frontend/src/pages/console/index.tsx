import { RouteObject } from "react-router-dom";
import ConsoleLayout from "../../components/layout/ConsoleLayout";
import { RouteError } from "../../components/common/errorBoundary";
import Dashboard from "./projectDashboard";
import Overview from "./overview";

export function consoleRoutes(): RouteObject {
  return {
    path: "",
    element: <ConsoleLayout />,
    children: [
      { path: "", element: <Overview /> },
      {
        path: "project/:projectId",
        element: <Dashboard />,
        errorElement: <RouteError />,
      },
    ],
  };
}
