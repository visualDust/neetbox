import React, { PropsWithChildren, useEffect } from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import AppLayout, { Home } from "./App";
import LoginPage from "./pages/login";
import "./index.css";
import Console, { consoleRoutes } from "./pages/console";
import { startBackgroundTasks } from "./services/projects";
import { ThemeContextProvider } from "./components/themeSwitcher";

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        path: "",
        // element: <Home />,
        element: <Console />,
      },
      consoleRoutes(),
      {
        path: "/login",
        element: <LoginPage />,
      },
    ],
  },
]);

function ServiceProvider({ children }: PropsWithChildren) {
  useEffect(() => {
    const tasks = startBackgroundTasks();
    return () => tasks.stop();
  });
  return children;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeContextProvider>
      <ServiceProvider>
        <RouterProvider router={router} />
      </ServiceProvider>
    </ThemeContextProvider>
  </React.StrictMode>,
);
