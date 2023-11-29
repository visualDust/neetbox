import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import LoginPage from "./pages/login";
import "./index.css";
import Console, { consoleRoutes } from "./pages/console";
import { ThemeContextProvider } from "./components/themeSwitcher";
import { ServiceProvider } from "./services/serviceProvider";

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

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeContextProvider>
      <ServiceProvider>
        <RouterProvider router={router} />
      </ServiceProvider>
    </ThemeContextProvider>
  </React.StrictMode>,
);
