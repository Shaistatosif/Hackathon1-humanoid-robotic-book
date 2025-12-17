import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Sidebar configuration for the Humanoid Robotics Textbook.
 *
 * Creating a sidebar enables you to:
 * - Create an ordered group of docs
 * - Render a sidebar for each doc of that group
 * - Provide next/previous navigation
 */
const sidebars: SidebarsConfig = {
  textbookSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Chapter 1: Introduction to Humanoid Robotics',
      link: {
        type: 'generated-index',
        description: 'Learn the fundamentals of humanoid robotics.',
      },
      collapsed: false,
      items: [
        'chapter-1/index',
      ],
    },
    {
      type: 'category',
      label: 'Chapter 2: Robot Components',
      link: {
        type: 'generated-index',
        description: 'Explore the key components that make up humanoid robots.',
      },
      items: [
        'chapter-2/index',
      ],
    },
    {
      type: 'category',
      label: 'Chapter 3: Sensors and Actuators',
      link: {
        type: 'generated-index',
        description: 'Understanding sensors and actuators in humanoid robots.',
      },
      items: [
        'chapter-3/index',
      ],
    },
  ],
};

export default sidebars;
