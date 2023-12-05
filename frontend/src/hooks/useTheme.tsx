import { createContext, useContext } from "react";

export const ThemeContext = createContext<{
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
}>(null!);

export function useTheme() {
  return useContext(ThemeContext);
}
