import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from '@/components/layout/AppLayout'
import AuthLayout from '@/components/layout/AuthLayout'

import LoginPage from '@/modules/auth/pages/LoginPage'
import SignupPage from '@/modules/auth/pages/SignupPage'
import ProfilePage from '@/modules/auth/pages/ProfilePage'

import ProjectsListPage from '@/modules/projects/pages/ProjectsListPage'
import ProjectDetailsPage from '@/modules/projects/pages/ProjectDetailsPage'
import ProjectIntegrationsPage from '@/modules/projects/pages/ProjectIntegrationsPage'

import MembersPage from '@/modules/members/pages/MembersPage'

import TasksListPage from '@/modules/tasks/pages/TasksListPage'
import TaskDetailsPage from '@/modules/tasks/pages/TaskDetailsPage'
import MyTasksPage from '@/modules/tasks/pages/MyTasksPage'

import ReviewsPage from '@/modules/reviews/pages/ReviewsPage'
import NotificationsPage from '@/modules/notifications/pages/NotificationsPage'
import AnalyticsPage from '@/modules/analytics/pages/AnalyticsPage'

export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/signup', element: <SignupPage /> },
    ],
  },
  {
    element: <AppLayout />,
    children: [
      { path: '/', element: <Navigate to="/projects" replace /> },
      { path: '/profile', element: <ProfilePage /> },
      { path: '/projects', element: <ProjectsListPage /> },
      { path: '/projects/:projectId', element: <ProjectDetailsPage /> },
      { path: '/projects/:projectId/integrations', element: <ProjectIntegrationsPage /> },
      { path: '/projects/:projectId/members', element: <MembersPage /> },
      { path: '/projects/:projectId/tasks', element: <TasksListPage /> },
      { path: '/projects/:projectId/tasks/:taskId', element: <TaskDetailsPage /> },
      { path: '/projects/:projectId/analytics', element: <AnalyticsPage /> },
      { path: '/my-tasks', element: <MyTasksPage /> },
      { path: '/reviews', element: <ReviewsPage /> },
      { path: '/notifications', element: <NotificationsPage /> },
      { path: '/analytics', element: <AnalyticsPage /> },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
])
