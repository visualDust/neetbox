import { RouteObject } from "react-router-dom";
import ConsoleLayout from "../../components/layout/ConsoleLayout";
import Dashboard from "./proejctDashboard";
import Overview from "./overview";

export function consoleRoutes(): RouteObject {
  return {
    path: "console",
    element: <ConsoleLayout />,
    children: [
      {
        path: "project/:projectName",
        element: <Dashboard />,
        errorElement: <div>Error</div>,
      },
      { path: "overview", element: <Overview /> },
    ],
  };
}
