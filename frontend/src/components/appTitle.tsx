import { atom, useAtom } from "jotai";
import { PropsWithChildren, ReactNode, useEffect } from "react";

const appTitle = atom("" as ReactNode);

export const useTitle = () => useAtom(appTitle)[0];

export const AppTitle = (props: PropsWithChildren) => {
  const [currentTitle, setTitle] = useAtom(appTitle);
  useEffect(() => {
    const prevTitle = currentTitle;
    return () => {
      setTitle(prevTitle);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    setTitle(props.children);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.children]);
  return null;
};
