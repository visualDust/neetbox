import { atom, useAtom } from "jotai";
import { PropsWithChildren, ReactNode, useEffect } from "react";

const appTitle = atom({ title: "" } as { title: ReactNode; extra?: ReactNode });

export const useTitle = () => useAtom(appTitle)[0];

export const AppTitle = (props: PropsWithChildren<{ extra?: ReactNode }>) => {
  const [currentTitle, setTitle] = useAtom(appTitle);
  useEffect(() => {
    const prevTitle = currentTitle;
    return () => {
      setTitle(prevTitle);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    setTitle({ title: props.children, extra: props.extra });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.children, props.extra]);
  return null;
};
