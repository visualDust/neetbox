import React, { useCallback, useEffect, useState } from "react";
import { Button } from "@douyinfe/semi-ui";
import { ThemeContext, useTheme } from "../hooks/useTheme";

export default function SwitchColorMode(): React.JSX.Element {
  const { darkMode, setDarkMode } = useTheme();
  const switchMode = () => {
    setDarkMode(!darkMode);
  };
  return <Button onClick={switchMode}>Switch Mode</Button>;
}

export function ThemeContextProvider(props: React.PropsWithChildren) {
  const [darkMode, setDarkModeState] = useState(false);

  const setDarkMode = useCallback((val) => {
    setDarkModeState(val);
    localStorage.setItem("neetbox-theme", val ? "dark" : "");
  }, []);

  useEffect(() => {
    setDarkModeState(localStorage.getItem("neetbox-theme") === "dark");
  }, []);

  useEffect(() => {
    const body = document.body;
    if (darkMode) {
      body.setAttribute("theme-mode", "dark");
    } else {
      body.removeAttribute("theme-mode");
    }
  }, [darkMode]);

  return (
    <ThemeContext.Provider value={{ darkMode, setDarkMode }}>
      {props.children}
    </ThemeContext.Provider>
  );
}
