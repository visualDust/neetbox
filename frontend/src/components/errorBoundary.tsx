import React, { ReactNode } from "react";
import { useRouteError } from "react-router";

export const RouteError = () => {
  const error = useRouteError();
  const text = `${error}\n\n${(error as Error)?.stack}`;
  return <pre style={{ whiteSpace: "pre-wrap", margin: 10 }}>{text}</pre>;
};

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{ renderError?: (error: Error, errorInfo: React.ErrorInfo) => ReactNode }>
> {
  state: { error?: Error; errorInfo?: React.ErrorInfo } = {};

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    this.setState({ error, errorInfo });
  }
  render(): React.ReactNode {
    return this.state.error
      ? this.props.renderError?.(this.state.error, this.state.errorInfo!) ?? this.renderDefaultErrorPage()
      : this.props.children;
  }

  renderDefaultErrorPage() {
    const text = `${this.state.error}\n\n${(this.state.error as Error)?.stack}\n\n${this.state.errorInfo
      ?.componentStack}`;
    return <pre style={{ whiteSpace: "pre-wrap", margin: 10 }}>{text}</pre>;
  }
}
