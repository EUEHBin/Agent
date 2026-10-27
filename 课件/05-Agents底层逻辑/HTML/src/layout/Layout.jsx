import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import NavBar from './NavBar.jsx'
import { NAV_ITEMS, APP_TITLE } from '../config/nav.js'
import './layout.css'

export default function Layout() {
  const { pathname } = useLocation()

  useEffect(() => {
    const item = NAV_ITEMS.find((i) => pathname.startsWith(i.path))
    document.title = item ? `${item.title} | ${APP_TITLE}` : APP_TITLE
  }, [pathname])

  return (
    <div className="shell">
      <NavBar />
      <main className="shell-main">
        <Outlet />
      </main>
    </div>
  )
}
