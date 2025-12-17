/**
 * Root component wrapper for Docusaurus.
 *
 * This component wraps the entire app and provides:
 * - Authentication context
 * - ChatWidget overlay
 * - RTL direction handling for Urdu locale
 */

import React, { useEffect } from 'react';
import { useLocation } from '@docusaurus/router';
import { AuthProvider } from '../context/AuthContext';
import ChatWidget from '../components/ChatWidget';

// Import RTL styles
import '../css/rtl.css';

interface RootProps {
  children: React.ReactNode;
}

// RTL locales
const RTL_LOCALES = ['ur', 'ar', 'fa', 'he'];

function getLocaleFromPath(pathname: string): string {
  // Extract locale from path like /ur/chapter-1
  const match = pathname.match(/^\/([a-z]{2})(\/|$)/);
  return match ? match[1] : 'en';
}

function RootContent({ children }: RootProps): JSX.Element {
  const location = useLocation();
  const locale = getLocaleFromPath(location.pathname);
  const isRTL = RTL_LOCALES.includes(locale);

  useEffect(() => {
    // Set direction on document root
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = locale === 'ur' ? 'ur-PK' : 'en-US';

    // Add/remove RTL class for additional styling hooks
    if (isRTL) {
      document.body.classList.add('rtl-locale');
    } else {
      document.body.classList.remove('rtl-locale');
    }

    return () => {
      document.body.classList.remove('rtl-locale');
    };
  }, [locale, isRTL]);

  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}

export default function Root({ children }: RootProps): JSX.Element {
  return (
    <AuthProvider>
      <RootContent>{children}</RootContent>
    </AuthProvider>
  );
}
