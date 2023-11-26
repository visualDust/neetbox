import React, { Component } from "react";
import Logo from "./logo";

export default function FooterContent(): React.JSX.Element {
  return (
    <div style={{ textAlign: "center" }}>
      <Logo styles={{ width: 50 }} withGlow={true} withLink={true} />
      <br />
      <div style={{ fontSize: 20 }}>
        © 2023 - 2023 Neet Design. All rights reserved.
      </div>
    </div>
  );
}
