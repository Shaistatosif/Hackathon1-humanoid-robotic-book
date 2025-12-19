/**
 * Homepage component for the Humanoid Robotics Textbook.
 *
 * Provides an engaging landing page with quick access to chapters.
 */

import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

interface FeatureItem {
  title: string;
  description: string;
  icon: string;
}

const features: FeatureItem[] = [
  {
    title: 'Comprehensive Content',
    description:
      'Professional, academically-rigorous content covering humanoid robot design, components, sensors, and control systems.',
    icon: '📚',
  },
  {
    title: 'AI-Powered Q&A',
    description:
      'Ask questions about any topic and receive accurate answers with citations to relevant sections.',
    icon: '🤖',
  },
  {
    title: 'Interactive Quizzes',
    description:
      'Test your understanding with chapter quizzes and track your learning progress.',
    icon: '📝',
  },
  {
    title: 'Bilingual Support',
    description:
      'Available in English and Urdu (اردو) with proper RTL layout support.',
    icon: '🌐',
  },
];

interface ChapterItem {
  number: number;
  title: string;
  description: string;
  slug: string;
  image: string;
}

const chapters: ChapterItem[] = [
  {
    number: 1,
    title: 'Introduction to Humanoid Robotics',
    description: 'Learn the fundamentals, history, and key characteristics of humanoid robots.',
    slug: '/chapter-1',
    image: '/img/chapters/chapter-1.svg',
  },
  {
    number: 2,
    title: 'Robot Components and Architecture',
    description: 'Explore hardware and software components that make up humanoid systems.',
    slug: '/chapter-2',
    image: '/img/chapters/chapter-2.svg',
  },
  {
    number: 3,
    title: 'Sensors and Actuators',
    description: 'Deep dive into sensing and actuation systems for perception and movement.',
    slug: '/chapter-3',
    image: '/img/chapters/chapter-3.svg',
  },
];

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <p className={styles.authorName}>By <strong>Shaista Tosif</strong></p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/chapter-1"
          >
            Start Learning
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            to="/"
          >
            Browse Contents
          </Link>
        </div>
      </div>
    </header>
  );
}

function Feature({ title, description, icon }: FeatureItem) {
  return (
    <div className={clsx('col col--3', styles.feature)}>
      <div className={styles.featureIcon}>{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function ChapterCard({ number, title, description, slug, image }: ChapterItem) {
  return (
    <Link to={slug} className={styles.chapterCard}>
      <div className={styles.chapterImageWrapper}>
        <img src={image} alt={`Chapter ${number}: ${title}`} className={styles.chapterImage} />
      </div>
      <div className={styles.chapterContent}>
        <div className={styles.chapterNumber}>Chapter {number}</div>
        <h3 className={styles.chapterTitle}>{title}</h3>
        <p className={styles.chapterDescription}>{description}</p>
        <span className={styles.chapterLink}>Read chapter →</span>
      </div>
    </Link>
  );
}

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="AI-Native Learning Platform for Humanoid Robotics"
    >
      <HomepageHeader />
      <main>
        {/* Features Section */}
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>

        {/* Chapters Section */}
        <section className={styles.chapters}>
          <div className="container">
            <h2 className={styles.sectionTitle}>Textbook Chapters</h2>
            <div className={styles.chapterGrid}>
              {chapters.map((chapter) => (
                <ChapterCard key={chapter.number} {...chapter} />
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className={styles.cta}>
          <div className="container">
            <h2>Ready to explore humanoid robotics?</h2>
            <p>
              Start with the fundamentals and progress through advanced topics
              at your own pace.
            </p>
            <Link
              className="button button--primary button--lg"
              to="/chapter-1"
            >
              Begin Chapter 1
            </Link>
          </div>
        </section>
      </main>
    </Layout>
  );
}
