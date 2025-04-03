import React, { useCallback, useLayoutEffect, useState } from "react";
import { flushSync } from "react-dom";
import { Switch } from "@douyinfe/semi-ui";
import { ThemeContext, useTheme } from "../hooks/useTheme";

export default function SwitchColorMode(): React.JSX.Element {
  const { darkMode, setDarkMode } = useTheme();
  const switchMode = (checked, e) => {
    setDarkMode(!checked, e.nativeEvent);
  };
  return (
    <Switch
      size="large"
      checkedText="😎"
      uncheckedText="🌚"
      checked={!darkMode}
      onChange={switchMode}
      style={{ backgroundColor: "var(--semi-color-default)" }}
    ></Switch>
  );
}

export function ThemeContextProvider(props: React.PropsWithChildren) {
  const [darkMode, setDarkModeState] = useState(() => localStorage.getItem("neetbox-theme") != "light");

  const setDarkMode = useCallback((val, mouseEvent) => {
    const setTheme = () => {
      setDarkModeState(val);
      localStorage.setItem("neetbox-theme", val ? "" : "light");
    };

    if (document.startViewTransition) {
      document.startViewTransition(() => {
        flushSync(() => {
          setTheme();
          document.documentElement.style.setProperty(
            "--page-theme-changing-origin",
            typeof mouseEvent?.x === "number" ? `${mouseEvent.x}px ${mouseEvent.y}px` : "",
          );
        });
      });
    } else {
      setTheme();
    }
  }, []);

  useLayoutEffect(() => {
    const body = document.body;
    if (darkMode) {
      body.setAttribute("theme-mode", "dark");
    } else {
      body.removeAttribute("theme-mode");
    }
  }, [darkMode]);

  return <ThemeContext.Provider value={{ darkMode, setDarkMode }}>{props.children}</ThemeContext.Provider>;
}
