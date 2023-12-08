import { atom, useAtom } from "jotai";
import { PropsWithChildren, ReactNode, useEffect } from "react";

const appTitle = atom([{ title: "" }] as Array<{ title: ReactNode; extra?: ReactNode }>);

export const useTitle = () => useAtom(appTitle)[0].at(-1);

export const AppTitle = (props: PropsWithChildren<{ extra?: ReactNode }>) => {
  const [_, setTitle] = useAtom(appTitle);
  useEffect(() => {
    setTitle((arr) => [...arr, { title: props.children, extra: props.extra }]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    return () => setTitle((arr) => arr.slice(0, -1));
  }, [props.children, props.extra, setTitle]);
  return null;
};
