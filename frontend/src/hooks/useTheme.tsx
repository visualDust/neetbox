import { createContext, useContext } from "react";

export const ThemeContext = createContext<{
  darkMode: boolean;
  setDarkMode: (val: boolean, mouseEvent?: Event) => void;
}>(null!);

export function useTheme() {
  return useContext(ThemeContext);
}
