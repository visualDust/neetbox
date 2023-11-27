import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { Button } from "@douyinfe/semi-ui";

const Context = createContext<{
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
}>(null!);

export function useTheme() {
  return useContext(Context);
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
    <Context.Provider value={{ darkMode, setDarkMode }}>
      {props.children}
    </Context.Provider>
  );
}

export default function SwitchColorMode(): React.JSX.Element {
  const { darkMode, setDarkMode } = useTheme();
  const switchMode = () => {
    setDarkMode(!darkMode);
  };
  return <Button onClick={switchMode}>Switch Mode</Button>;
}
