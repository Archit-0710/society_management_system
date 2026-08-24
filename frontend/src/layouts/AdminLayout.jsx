import { Shell } from './ResidentLayout'

const links = [['/admin', 'Dashboard', true], ['/admin/complaints', 'Complaints'], ['/admin/categories', 'Categories'], ['/admin/notices', 'Notices'], ['/admin/notifications', 'Notifications']]

export function AdminLayout() {
  return <Shell title="Administration" links={links} />
}
