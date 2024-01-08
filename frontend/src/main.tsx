import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import { LocaleProvider } from "@douyinfe/semi-ui";
import en_US from "@douyinfe/semi-ui/lib/es/locale/source/en_US";
import LoginPage from "./pages/login";
import "./index.css";
import { consoleRoutes } from "./pages/console";
import { ThemeContextProvider } from "./components/themeSwitcher";
import { ServiceProvider } from "./services/serviceProvider";
import App from "./App";
import { RouteError } from "./components/common/errorBoundary";

const router = createBrowserRouter(
  [
    {
      path: "/",
      element: <App />,
      errorElement: <RouteError />,
      children: [
        // {
        //   path: "",
        //   element: <Home />,
        // },
        consoleRoutes(),
        {
          path: "/login",
          element: <LoginPage />,
        },
      ],
    },
  ],
  { basename: "/web/" },
);

if (process.env.NODE_ENV === "development") {
  if (window.location.pathname == "/") {
    // For dev only. This is bad because it restarts the whole page/script loading process.
    // In production it's done by server redirect.
    window.location.replace("/web/");
  }
}

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
