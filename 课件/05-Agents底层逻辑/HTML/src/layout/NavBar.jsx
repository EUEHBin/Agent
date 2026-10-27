import { NavLink } from 'react-router-dom'
import { NAV_ITEMS } from '../config/nav.js'

export default function NavBar() {
  return (
    <header className="nav">
      <div className="nav-brand">
        <span className="nav-glyph" />
        <span className="nav-title">神经网络 · 交互实验室</span>
      </div>
      <nav className="nav-menu">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
          >
            <i className={item.icon} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
