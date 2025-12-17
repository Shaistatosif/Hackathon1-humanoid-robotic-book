import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/Hackathon1-humanoid-robotic-book/ur/dashboard',
    component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/dashboard', 'ba2'),
    exact: true
  },
  {
    path: '/Hackathon1-humanoid-robotic-book/ur/login',
    component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/login', 'b0d'),
    exact: true
  },
  {
    path: '/Hackathon1-humanoid-robotic-book/ur/quiz',
    component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/quiz', 'cbe'),
    exact: true
  },
  {
    path: '/Hackathon1-humanoid-robotic-book/ur/quiz/chapter-1',
    component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/quiz/chapter-1', 'fa0'),
    exact: true
  },
  {
    path: '/Hackathon1-humanoid-robotic-book/ur/quiz/chapter-2',
    component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/quiz/chapter-2', '35e'),
    exact: true
  },
  {
    path: '/Hackathon1-humanoid-robotic-book/ur/quiz/chapter-3',
    component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/quiz/chapter-3', '4bf'),
    exact: true
  },
  {
    path: '/Hackathon1-humanoid-robotic-book/ur/register',
    component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/register', '150'),
    exact: true
  },
  {
    path: '/Hackathon1-humanoid-robotic-book/ur/',
    component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/', '63b'),
    exact: true
  },
  {
    path: '/Hackathon1-humanoid-robotic-book/ur/',
    component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/', '785'),
    routes: [
      {
        path: '/Hackathon1-humanoid-robotic-book/ur/',
        component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/', '44f'),
        routes: [
          {
            path: '/Hackathon1-humanoid-robotic-book/ur/',
            component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/', '048'),
            routes: [
              {
                path: '/Hackathon1-humanoid-robotic-book/ur/category/chapter-1-introduction-to-humanoid-robotics',
                component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/category/chapter-1-introduction-to-humanoid-robotics', 'cda'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/Hackathon1-humanoid-robotic-book/ur/category/chapter-2-robot-components',
                component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/category/chapter-2-robot-components', '8ea'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/Hackathon1-humanoid-robotic-book/ur/category/chapter-3-sensors-and-actuators',
                component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/category/chapter-3-sensors-and-actuators', 'b4b'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/Hackathon1-humanoid-robotic-book/ur/chapter-1',
                component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/chapter-1', 'e23'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/Hackathon1-humanoid-robotic-book/ur/chapter-2',
                component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/chapter-2', '02f'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/Hackathon1-humanoid-robotic-book/ur/chapter-3',
                component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/chapter-3', '962'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/Hackathon1-humanoid-robotic-book/ur/intro',
                component: ComponentCreator('/Hackathon1-humanoid-robotic-book/ur/intro', '4ea'),
                exact: true,
                sidebar: "textbookSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
