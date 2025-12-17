/**
 * Custom DocItem Layout with Summary component.
 *
 * Extends the default Docusaurus DocItem Layout to include
 * AI-generated chapter summaries for chapter pages.
 */

import React from 'react';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import DocItemLayout from '@theme-original/DocItem/Layout';
import type DocItemLayoutType from '@theme/DocItem/Layout';
import type { WrapperProps } from '@docusaurus/types';
import Summary from '../../../components/Summary';

type Props = WrapperProps<typeof DocItemLayoutType>;

/**
 * Extract chapter ID from document metadata.
 */
function getChapterId(docId: string): string | null {
  // Match patterns like "chapter-1/index" or "chapter-1"
  const match = docId.match(/^(chapter-\d+)/);
  return match ? match[1] : null;
}

export default function DocItemLayoutWrapper(props: Props): JSX.Element {
  const { metadata } = useDoc();
  const chapterId = getChapterId(metadata.id);

  return (
    <>
      <DocItemLayout {...props} />
      {chapterId && (
        <div className="container margin-top--lg margin-bottom--lg">
          <Summary chapterId={chapterId} />
        </div>
      )}
    </>
  );
}
