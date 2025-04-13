import { useRef, useEffect, HTMLAttributes, useState } from "react";
import * as echarts from "echarts";
import { IdleTimer } from "../../utils/timer";
import { useTheme } from "../../hooks/useTheme";
import Loading from "./loading";

export interface EChartsProps {
  initialOption: () => echarts.EChartsOption;
  updatingOption: () => echarts.EChartsOption;
  style?: HTMLAttributes<HTMLElement>["style"];
}

// convert RGB to HEX
export function rgbToHex(rgb: string): string {
  const match = rgb.match(/\d+/g);
  if (!match || match.length < 3) return rgb;

  const r = parseInt(match[0]).toString(16).padStart(2, "0");
  const g = parseInt(match[1]).toString(16).padStart(2, "0");
  const b = parseInt(match[2]).toString(16).padStart(2, "0");

  return `#${r}${g}${b}`;
}

// get semi colors for data series and convert to HEX
export function getSemiColorDataHexColors(shuffle = false): string[] {
  const styles = getComputedStyle(document.body);
  const colors: string[] = [];

  for (let i = 0; i < 20; i++) {
    const cssVarName = `--semi-color-data-${i}`;
    const value = styles.getPropertyValue(cssVarName).trim();
    const hex = value.startsWith("rgb") ? rgbToHex(value) : value;
    colors.push(hex);
  }

  return shuffle ? colors.sort(() => Math.random() - 0.5) : colors;
}

export const ECharts = (props: EChartsProps) => {
  const chartContainerRef = useRef(null);
  const [echartsModule, setEchartsModule] = useState<typeof echarts | null>(null);
  const [echartsInstance, setEChartsInstance] = useState<echarts.ECharts | null>(null);
  const { darkMode } = useTheme();

  useEffect(() => {
    import("echarts").then((mod) => {
      // setEchartsModule(mod);
      new IdleTimer(() => setEchartsModule(mod)).schedule(1000);
    });
  });

  useEffect(() => {
    if (echartsModule) {
      const chart = echartsModule.init(
        chartContainerRef.current,
        darkMode ? "dark" : null,
        // { renderer: "svg" },
      );

      chart.setOption(props.initialOption(), false, true);
      setEChartsInstance(chart);

      const resizeTimer = new IdleTimer(() => chart?.resize());
      const handleResize = () => {
        resizeTimer.schedule(100);
      };
      const resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(chartContainerRef.current!);

      return () => {
        resizeObserver.disconnect();
        chart?.dispose();
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [echartsModule, darkMode]);

  useEffect(() => {
    if (echartsInstance) {
      echartsInstance.setOption(props.updatingOption());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [echartsInstance, props.updatingOption]);

  return echartsModule ? (
    <div ref={chartContainerRef} style={props.style} />
  ) : (
    <Loading width={props.style?.width as string} height={props.style?.height as string} />
  );
};
