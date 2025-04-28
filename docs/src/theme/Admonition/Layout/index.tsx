import React, {type ReactNode} from 'react';
import Layout from '@theme-original/Admonition/Layout';
import type LayoutType from '@theme/Admonition/Layout';
import type {WrapperProps} from '@docusaurus/types';
import { Analytics } from "@vercel/analytics/react"

type Props = WrapperProps<typeof LayoutType>;

export default function LayoutWrapper(props: Props): ReactNode {
  return (
    <>
      <Analytics /> {/* Vercel Analytics */}
      <Layout {...props} />
    </>
  );
}
